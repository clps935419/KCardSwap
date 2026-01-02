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
from app.modules.social.application.use_cases.cards.confirm_upload import (
    ConfirmCardUploadUseCase,
)
from app.modules.social.application.use_cases.cards.delete_card import DeleteCardUseCase
from app.modules.social.application.use_cases.cards.get_my_cards import (
    GetMyCardsUseCase,
)
from app.modules.social.application.use_cases.cards.upload_card import (
    UploadCardUseCase,
)
from app.modules.social.domain.repositories.i_card_repository import ICardRepository
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
    CardListResponseWrapper,
    CardResponse,
    CardResponseWrapper,
    DeleteSuccessResponse,
    DeleteSuccessResponseWrapper,
    QuotaStatusResponse,
    QuotaStatusResponseWrapper,
    UploadCardRequest,
    UploadUrlResponse,
    UploadUrlResponseWrapper,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.infrastructure.external.storage_service_factory import (
    get_storage_service,
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
    response_model=UploadUrlResponseWrapper,
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
) -> UploadUrlResponseWrapper:
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
    card_repo: ICardRepository = CardRepositoryImpl(session)
    validation_service = CardValidationService()
    gcs_service = get_storage_service()

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

        data = UploadUrlResponse(
            upload_url=result.upload_url,
            method=result.method,
            required_headers=result.required_headers,
            image_url=result.image_url,
            expires_at=result.expires_at,
            card_id=result.card_id,
        )
        return UploadUrlResponseWrapper(data=data, meta=None, error=None)
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
    response_model=CardListResponseWrapper,
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
) -> CardListResponseWrapper:
    """
    Get all cards owned by the current user.

    Optionally filter by card status.
    """
    # Initialize dependencies
    card_repo: ICardRepository = CardRepositoryImpl(session)

    # Create and execute use case
    use_case = GetMyCardsUseCase(card_repository=card_repo)
    cards = await use_case.execute(owner_id=current_user_id, status=status_filter)

    # Convert to response
    data = [
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
    
    return CardListResponseWrapper(data=data, meta=None, error=None)


@router.delete(
    "/{card_id}",
    response_model=DeleteSuccessResponseWrapper,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Card deleted successfully"},
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
) -> DeleteSuccessResponseWrapper:
    """
    Delete a card.

    Only the owner can delete their own cards.
    Cards in active trades cannot be deleted.
    """
    # Initialize dependencies
    card_repo: ICardRepository = CardRepositoryImpl(session)
    gcs_service = get_storage_service()

    # Create and execute use case
    use_case = DeleteCardUseCase(card_repository=card_repo, gcs_service=gcs_service)

    try:
        deleted = await use_case.execute(card_id=card_id, owner_id=current_user_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Card not found or not owner"},
            )
        
        data = DeleteSuccessResponse(success=True, message="Card deleted successfully")
        return DeleteSuccessResponseWrapper(data=data, meta=None, error=None)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(e)},
        )


@router.get(
    "/quota/status",
    response_model=QuotaStatusResponseWrapper,
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
) -> QuotaStatusResponseWrapper:
    """
    Get current quota status for the user.

    Shows:
    - Uploads today / daily limit
    - Storage used / storage limit
    - Remaining uploads and storage
    """
    # Initialize dependencies
    card_repo: ICardRepository = CardRepositoryImpl(session)

    # Create and execute use case
    use_case = CheckUploadQuotaUseCase(card_repository=card_repo)
    status_result = await use_case.execute(owner_id=current_user_id, quota=quota)

    data = QuotaStatusResponse(**status_result.to_dict())
    return QuotaStatusResponseWrapper(data=data, meta=None, error=None)


@router.post(
    "/{card_id}/confirm-upload",
    response_model=DeleteSuccessResponseWrapper,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Upload confirmed successfully"},
        400: {"description": "Invalid request (already confirmed, no image, etc.)"},
        401: {"description": "Unauthorized"},
        403: {"description": "Not the card owner"},
        404: {"description": "Card not found or image not found in storage"},
    },
    summary="Confirm card upload",
    description="Confirm that the card image has been successfully uploaded to GCS after using the signed URL",
)
async def confirm_card_upload(
    card_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DeleteSuccessResponseWrapper:
    """
    Confirm card upload after successful GCS upload.

    This endpoint should be called after the client successfully uploads
    the image file to the signed URL provided by /upload-url endpoint.

    It will:
    1. Verify that the card exists and belongs to the user
    2. Check that the image file exists in GCS
    3. Mark the card's upload status as "confirmed"

    This prevents "ghost records" where cards are created but images
    are never actually uploaded.
    """
    # Initialize dependencies
    card_repo: ICardRepository = CardRepositoryImpl(session)
    gcs_service = get_storage_service()

    # Create and execute use case
    use_case = ConfirmCardUploadUseCase(
        card_repository=card_repo,
        gcs_service=gcs_service,
    )

    try:
        await use_case.execute(card_id=card_id, owner_id=current_user_id)
        data = DeleteSuccessResponse(success=True, message="Upload confirmed successfully")
        return DeleteSuccessResponseWrapper(data=data, meta=None, error=None)
    except ValueError as e:
        error_message = str(e)

        # Determine appropriate HTTP status code
        if "not found" in error_message.lower():
            if (
                "image file" in error_message.lower()
                or "storage" in error_message.lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "IMAGE_NOT_FOUND",
                        "message": error_message,
                    },
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "CARD_NOT_FOUND",
                        "message": "Card not found",
                    },
                )
        elif "not authorized" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Not authorized to confirm this card",
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": error_message,
                },
            )
