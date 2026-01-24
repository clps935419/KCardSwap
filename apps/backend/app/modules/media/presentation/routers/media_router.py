"""Media router - API endpoints for media upload and attachment."""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from injector import Injector

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
from app.modules.media.presentation.schemas.media_schemas import (
    AttachMediaResponseSchema,
    AttachMediaToGalleryCardRequestSchema,
    AttachMediaToPostRequestSchema,
    ConfirmUploadResponseSchema,
    CreateUploadUrlRequestSchema,
    CreateUploadUrlResponseSchema,
)
from app.shared.presentation.deps.injector import get_injector
from app.shared.presentation.deps.require_user import get_current_user_id

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
    user_id: UUID = Depends(get_current_user_id),
    injector: Injector = Depends(get_injector),
):
    """Generate presigned upload URL for media.
    
    Flow: presign → upload (client to GCS) → confirm → attach
    
    Returns:
        Presigned URL and media_id for subsequent confirmation
    """
    use_case = injector.get(CreateUploadUrlUseCase)
    
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
    user_id: UUID = Depends(get_current_user_id),
    injector: Injector = Depends(get_injector),
):
    """Confirm media upload and apply quota.
    
    Flow: presign → upload (client to GCS) → confirm → attach
    
    Raises:
        LimitExceededException: If quota is exceeded (422)
        ValueError: If media not found or not owned by user (400)
    """
    use_case = injector.get(ConfirmUploadUseCase)
    
    result = await use_case.execute(
        ConfirmUploadRequest(
            user_id=user_id,
            media_id=media_id,
        )
    )

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
    user_id: UUID = Depends(get_current_user_id),
    injector: Injector = Depends(get_injector),
):
    """Attach confirmed media to post.
    
    Flow: presign → upload (client to GCS) → confirm → attach
    
    Only confirmed media owned by the user can be attached.
    """
    use_case = injector.get(AttachMediaUseCase)
    
    result = await use_case.execute(
        AttachMediaRequest(
            user_id=user_id,
            media_id=request.media_id,
            target_type="post",
            target_id=post_id,
        )
    )

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
    user_id: UUID = Depends(get_current_user_id),
    injector: Injector = Depends(get_injector),
):
    """Attach confirmed media to gallery card.
    
    Flow: presign → upload (client to GCS) → confirm → attach
    
    Only confirmed media owned by the user can be attached.
    """
    use_case = injector.get(AttachMediaUseCase)
    
    result = await use_case.execute(
        AttachMediaRequest(
            user_id=user_id,
            media_id=request.media_id,
            target_type="gallery_card",
            target_id=card_id,
        )
    )

    return AttachMediaResponseSchema(
        media_id=result.media_id,
        status=result.status,
        attached_to=result.attached_to,
        target_id=result.target_id,
    )
