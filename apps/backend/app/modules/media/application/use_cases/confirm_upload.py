"""Confirm upload use case - Confirm step of media upload flow."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.modules.media.domain.entities.media_asset import MediaAsset
from app.modules.media.domain.repositories.i_media_repository import IMediaRepository
from app.shared.domain.quota.media_quota_service import MediaQuotaService
from app.shared.infrastructure.external.gcs_storage_service import GCSStorageService


@dataclass
class ConfirmUploadRequest:
    """Request for confirming upload."""
    user_id: UUID
    media_id: UUID


@dataclass
class ConfirmUploadResponse:
    """Response after confirming upload."""
    media_id: UUID
    status: str
    gcs_blob_name: str
    file_size_bytes: int


class ConfirmUploadUseCase:
    """Use case for confirming media upload.
    
    This is step 2 of the media upload flow: presign → upload → confirm → attach.
    
    FR-007: Only confirmed media can be attached.
    FR-022: Quota is applied ONLY at this stage (not at presign).
    T052: Apply media quota in confirm use case.
    """

    def __init__(
        self,
        media_repository: IMediaRepository,
        media_quota_service: MediaQuotaService,
        storage_service: GCSStorageService,
    ):
        self.media_repository = media_repository
        self.media_quota_service = media_quota_service
        self.storage_service = storage_service

    async def execute(self, request: ConfirmUploadRequest) -> ConfirmUploadResponse:
        """Confirm media upload and apply quota.
        
        Args:
            request: Confirmation request
            
        Returns:
            Confirmed media details
            
        Raises:
            ValueError: If media not found or not owned by user
            LimitExceededException: If quota is exceeded
        """
        # Get media asset
        media = await self.media_repository.get_by_id(request.media_id)
        if not media:
            raise ValueError(f"Media {request.media_id} not found")

        # Verify ownership
        if not media.is_owned_by(request.user_id):
            raise ValueError(f"Media {request.media_id} is not owned by user {request.user_id}")

        # Verify blob exists in GCS
        if not self.storage_service.blob_exists(media.gcs_blob_name):
            raise ValueError(f"Media file not found in storage: {media.gcs_blob_name}")

        # FR-022 + T052: Apply media quotas
        # 1. Check file size limit
        await self.media_quota_service.check_file_size(
            user_id=request.user_id,
            file_size_bytes=media.file_size_bytes,
        )

        # 2. Check monthly bytes quota
        now = datetime.utcnow()
        current_month_bytes = await self.media_repository.get_monthly_bytes_used(
            user_id=request.user_id,
            year=now.year,
            month=now.month,
        )
        
        await self.media_quota_service.check_monthly_bytes(
            user_id=request.user_id,
            current_bytes_used=current_month_bytes,
            additional_bytes=media.file_size_bytes,
        )

        # Confirm the upload
        media.confirm()

        # Update in database
        await self.media_repository.update(media)

        return ConfirmUploadResponse(
            media_id=media.id,
            status=media.status.value,
            gcs_blob_name=media.gcs_blob_name,
            file_size_bytes=media.file_size_bytes,
        )
