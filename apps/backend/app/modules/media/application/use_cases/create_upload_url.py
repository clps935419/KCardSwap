"""Create upload URL use case - Presign step of media upload flow."""
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from app.modules.media.domain.entities.media_asset import MediaAsset, MediaStatus
from app.modules.media.domain.repositories.i_media_repository import IMediaRepository
from app.shared.infrastructure.external.gcs_storage_service import GCSStorageService


@dataclass
class CreateUploadUrlRequest:
    """Request for creating upload URL."""
    user_id: UUID
    content_type: str
    file_size_bytes: int
    filename: Optional[str] = None  # Original filename for reference


@dataclass
class CreateUploadUrlResponse:
    """Response containing presigned upload URL and media ID."""
    media_id: UUID
    upload_url: str
    gcs_blob_name: str
    expires_in_minutes: int


class CreateUploadUrlUseCase:
    """Use case for generating presigned upload URLs.
    
    This is step 1 of the media upload flow: presign → upload → confirm → attach.
    
    FR-006: System must support media upload through presigned URL flow.
    FR-022: Quota is NOT applied at this stage (only on confirm).
    """

    def __init__(
        self,
        media_repository: IMediaRepository,
        storage_service: GCSStorageService,
    ):
        self.media_repository = media_repository
        self.storage_service = storage_service

    async def execute(self, request: CreateUploadUrlRequest) -> CreateUploadUrlResponse:
        """Generate presigned upload URL for user.
        
        Args:
            request: Upload URL request
            
        Returns:
            Presigned URL and media ID for subsequent confirmation
        """
        # Generate unique media ID and blob name
        media_id = uuid.uuid4()
        
        # Determine file extension from content type
        extension = self._get_extension_from_content_type(request.content_type)
        
        # Create GCS blob name: media/{user_id}/{media_id}.{ext}
        blob_name = f"media/{request.user_id}/{media_id}{extension}"

        # Create media asset in PENDING status
        media = MediaAsset(
            id=media_id,
            owner_id=request.user_id,
            gcs_blob_name=blob_name,
            content_type=request.content_type,
            file_size_bytes=request.file_size_bytes,
            status=MediaStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )

        # Save to database
        await self.media_repository.create(media)

        # Generate presigned upload URL
        expiration_minutes = 15
        upload_url = self.storage_service.generate_upload_signed_url(
            blob_name=blob_name,
            content_type=request.content_type,
            expiration_minutes=expiration_minutes,
        )

        return CreateUploadUrlResponse(
            media_id=media_id,
            upload_url=upload_url,
            gcs_blob_name=blob_name,
            expires_in_minutes=expiration_minutes,
        )

    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from content type."""
        mapping = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        return mapping.get(content_type.lower(), ".jpg")
