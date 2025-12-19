"""
Cards Router for Social Module
Handles card upload, retrieval, and deletion
"""

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id
from app.modules.social.application.use_cases.cards.check_quota import (
    CheckUploadQuotaUseCase,
)
from app.modules.social.application.use_cases.cards.delete_card import DeleteCardUseCase
from app.modules.social.application.use_cases.cards.get_my_cards import (
    GetMyCardsUseCase,
)
from app.modules.social.application.use_cases.cards.upload_card import (
    UploadCardUseCase,
)
from app.modules.social.domain.repositories.card_repository import CardRepository
from app.modules.social.domain.services.card_validation_service import (
    CardValidationService,
)
from app.modules.social.domain.value_objects.upload_quota import (
    QuotaExceeded,
    UploadQuota,
)
from app.modules.social.infrastructure.repositories.card_repository_impl import (
    CardRepositoryImpl,
)
from app.modules.social.presentation.schemas.card_schemas import (
    CardResponse,
    QuotaStatusResponse,
    UploadCardRequest,
    UploadUrlResponse,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.infrastructure.external.storage_service_factory import (
    storage_service_factory,
)

# Create router
router = APIRouter(prefix="/cards", tags=["Cards"])


def get_user_quota() -> UploadQuota:
    """
    Get upload quota based on user's subscription.
    TODO: Integrate with subscription system in Phase 8
    For now, return free tier quota for all users.
    """
    return UploadQuota.from_mb_gb(
        daily_limit=settings.DAILY_UPLOAD_LIMIT_FREE,
        max_file_mb=settings.MAX_FILE_SIZE_MB,
        total_storage_gb=settings.TOTAL_STORAGE_GB_FREE,
    )


@router.post(
    "/upload-url",
    response_model=UploadUrlResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Upload URL generated successfully"},
        400: {"description": "Invalid request (file type/size)"},
        401: {"description": "Unauthorized"},
        422: {"description": "Quota exceeded"},
    },
    summary="Get upload signed URL",
    description="Generate a signed URL for uploading a card image to GCS",
)
async def get_upload_url(
    request: UploadCardRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    quota: Annotated[UploadQuota, Depends(get_user_quota)],
) -> UploadUrlResponse:
    """
    Get a signed URL for uploading a card image.

    This endpoint:
    1. Validates file type and size
    2. Checks upload quotas (daily limit, storage limit)
    3. Creates a card record in the database
    4. Generates a GCS signed URL for upload

    After receiving the signed URL, the client should:
    1. Upload the file directly to GCS using PUT method
    2. Include the required Content-Type header
    """
    # Initialize dependencies
    card_repo: CardRepository = CardRepositoryImpl(session)
    validation_service = CardValidationService()
    gcs_service = storage_service_factory()

    # Create and execute use case
    use_case = UploadCardUseCase(
        card_repository=card_repo,
        validation_service=validation_service,
        gcs_service=gcs_service,
    )

    try:
        result = await use_case.execute(
            owner_id=current_user_id,
            content_type=request.content_type,
            file_size_bytes=request.file_size_bytes,
            quota=quota,
            idol=request.idol,
            idol_group=request.idol_group,
            album=request.album,
            version=request.version,
            rarity=request.rarity,
        )

        return UploadUrlResponse(
            upload_url=result.upload_url,
            method=result.method,
            required_headers=result.required_headers,
            image_url=result.image_url,
            expires_at=result.expires_at,
            card_id=result.card_id,
        )
    except QuotaExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "LIMIT_EXCEEDED",
                "message": e.reason,
                "limit_type": e.limit_type,
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(e)},
        )


@router.get(
    "/me",
    response_model=List[CardResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Cards retrieved successfully"},
        401: {"description": "Unauthorized"},
    },
    summary="Get my cards",
    description="Retrieve all cards owned by the authenticated user",
)
async def get_my_cards(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status_filter: Optional[str] = Query(
        None, description="Filter by status (available/trading/traded)"
    ),
) -> List[CardResponse]:
    """
    Get all cards owned by the current user.

    Optionally filter by card status.
    """
    # Initialize dependencies
    card_repo: CardRepository = CardRepositoryImpl(session)

    # Create and execute use case
    use_case = GetMyCardsUseCase(card_repository=card_repo)
    cards = await use_case.execute(owner_id=current_user_id, status=status_filter)

    # Convert to response
    return [
        CardResponse(
            id=card.id,
            owner_id=card.owner_id,
            idol=card.idol,
            idol_group=card.idol_group,
            album=card.album,
            version=card.version,
            rarity=card.rarity,
            status=card.status,
            image_url=card.image_url,
            size_bytes=card.size_bytes,
            created_at=card.created_at,
            updated_at=card.updated_at,
        )
        for card in cards
    ]


@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Card deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Not the card owner"},
        404: {"description": "Card not found"},
    },
    summary="Delete a card",
    description="Delete a card owned by the authenticated user",
)
async def delete_card(
    card_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """
    Delete a card.

    Only the owner can delete their own cards.
    Cards in active trades cannot be deleted.
    """
    # Initialize dependencies
    card_repo: CardRepository = CardRepositoryImpl(session)
    gcs_service = storage_service_factory()

    # Create and execute use case
    use_case = DeleteCardUseCase(card_repository=card_repo, gcs_service=gcs_service)

    try:
        deleted = await use_case.execute(card_id=card_id, owner_id=current_user_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Card not found or not owner"},
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(e)},
        )


@router.get(
    "/quota/status",
    response_model=QuotaStatusResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Quota status retrieved successfully"},
        401: {"description": "Unauthorized"},
    },
    summary="Get quota status",
    description="Check current upload quota usage",
)
async def get_quota_status(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    quota: Annotated[UploadQuota, Depends(get_user_quota)],
) -> QuotaStatusResponse:
    """
    Get current quota status for the user.

    Shows:
    - Uploads today / daily limit
    - Storage used / storage limit
    - Remaining uploads and storage
    """
    # Initialize dependencies
    card_repo: CardRepository = CardRepositoryImpl(session)

    # Create and execute use case
    use_case = CheckUploadQuotaUseCase(card_repository=card_repo)
    status_result = await use_case.execute(owner_id=current_user_id, quota=quota)

    return QuotaStatusResponse(**status_result.to_dict())
