"""Media router - API endpoints for media upload and attachment."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.media.application.use_cases.attach_media import (
    AttachMediaRequest,
    AttachMediaUseCase,
)
from app.modules.media.application.use_cases.confirm_upload import (
    ConfirmUploadRequest,
    ConfirmUploadUseCase,
)
from app.modules.media.application.use_cases.create_upload_url import (
    CreateUploadUrlRequest,
    CreateUploadUrlUseCase,
)
from app.modules.media.infrastructure.repositories.media_repository_impl import (
    MediaRepositoryImpl,
)
from app.modules.media.presentation.schemas.media_schemas import (
    AttachMediaResponseSchema,
    AttachMediaToGalleryCardRequestSchema,
    AttachMediaToPostRequestSchema,
    ConfirmUploadResponseSchema,
    CreateUploadUrlRequestSchema,
    CreateUploadUrlResponseSchema,
)
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)
from app.shared.domain.quota.media_quota_service import MediaQuotaService
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.infrastructure.external.storage_service_factory import (
    get_storage_service,
)
from app.shared.presentation.dependencies.services import get_subscription_service
from app.shared.presentation.deps.require_user import get_current_user_id
from app.shared.presentation.errors.limit_exceeded import LimitExceededException

router = APIRouter(prefix="/media", tags=["media"])


@router.post(
    "/upload-url",
    response_model=CreateUploadUrlResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Generate presigned upload URL",
    description="Step 1: Generate a presigned URL for uploading media to GCS. FR-006.",
)
async def create_upload_url(
    request: CreateUploadUrlRequestSchema,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: UUID = Depends(get_current_user_id),
):
    """Generate presigned upload URL for media.
    
    Flow: presign → upload (client to GCS) → confirm → attach
    
    Returns:
        Presigned URL and media_id for subsequent confirmation
    """
    media_repository = MediaRepositoryImpl(session)
    storage_service = get_storage_service()
    use_case = CreateUploadUrlUseCase(
        media_repository=media_repository,
        storage_service=storage_service,
    )
    
    result = await use_case.execute(
        CreateUploadUrlRequest(
            user_id=user_id,
            content_type=request.content_type,
            file_size_bytes=request.file_size_bytes,
            filename=request.filename,
        )
    )

    return CreateUploadUrlResponseSchema(
        media_id=result.media_id,
        upload_url=result.upload_url,
        expires_in_minutes=result.expires_in_minutes,
    )


@router.post(
    "/{media_id}/confirm",
    response_model=ConfirmUploadResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Confirm media upload",
    description="Step 2: Confirm that media was uploaded to GCS. Applies quota. FR-022, T052.",
)
async def confirm_upload(
    media_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    subscription_service: Annotated[
        ISubscriptionQueryService, Depends(get_subscription_service)
    ],
    user_id: UUID = Depends(get_current_user_id),
):
    """Confirm media upload and apply quota.
    
    Flow: presign → upload (client to GCS) → confirm → attach
    
    Raises:
        LimitExceededException: If quota is exceeded (422)
        ValueError: If media not found or not owned by user (400)
    """
    media_repository = MediaRepositoryImpl(session)
    storage_service = get_storage_service()
    media_quota_service = MediaQuotaService(subscription_service)
    use_case = ConfirmUploadUseCase(
        media_repository=media_repository,
        media_quota_service=media_quota_service,
        storage_service=storage_service,
    )
    
    try:
        result = await use_case.execute(
            ConfirmUploadRequest(
                user_id=user_id,
                media_id=media_id,
            )
        )
    except LimitExceededException as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message)
    except ValueError as exc:
        error_message = str(exc).lower()
        if "not found" in error_message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        if "not owned" in error_message or "only owner" in error_message:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return ConfirmUploadResponseSchema(
        media_id=result.media_id,
        status=result.status,
        file_size_bytes=result.file_size_bytes,
    )


@router.post(
    "/posts/{post_id}/attach",
    response_model=AttachMediaResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Attach media to post",
    description="Step 3: Attach confirmed media to a post. FR-007.",
)
async def attach_media_to_post(
    post_id: UUID,
    request: AttachMediaToPostRequestSchema,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: UUID = Depends(get_current_user_id),
):
    """Attach confirmed media to post.
    
    Flow: presign → upload (client to GCS) → confirm → attach
    
    Only confirmed media owned by the user can be attached.
    """
    media_repository = MediaRepositoryImpl(session)
    use_case = AttachMediaUseCase(media_repository=media_repository)
    
    try:
        result = await use_case.execute(
            AttachMediaRequest(
                user_id=user_id,
                media_id=request.media_id,
                target_type="post",
                target_id=post_id,
            )
        )
    except ValueError as exc:
        error_message = str(exc).lower()
        if "not found" in error_message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        if "not owned" in error_message or "only owner" in error_message:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return AttachMediaResponseSchema(
        media_id=result.media_id,
        status=result.status,
        attached_to=result.attached_to,
        target_id=result.target_id,
    )


@router.post(
    "/gallery/cards/{card_id}/attach",
    response_model=AttachMediaResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Attach media to gallery card",
    description="Step 3: Attach confirmed media to a gallery card. FR-007, FR-020.",
)
async def attach_media_to_gallery_card(
    card_id: UUID,
    request: AttachMediaToGalleryCardRequestSchema,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: UUID = Depends(get_current_user_id),
):
    """Attach confirmed media to gallery card.
    
    Flow: presign → upload (client to GCS) → confirm → attach
    
    Only confirmed media owned by the user can be attached.
    """
    media_repository = MediaRepositoryImpl(session)
    use_case = AttachMediaUseCase(media_repository=media_repository)
    
    try:
        result = await use_case.execute(
            AttachMediaRequest(
                user_id=user_id,
                media_id=request.media_id,
                target_type="gallery_card",
                target_id=card_id,
            )
        )
    except ValueError as exc:
        error_message = str(exc).lower()
        if "not found" in error_message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        if "not owned" in error_message or "only owner" in error_message:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return AttachMediaResponseSchema(
        media_id=result.media_id,
        status=result.status,
        attached_to=result.attached_to,
        target_id=result.target_id,
    )
