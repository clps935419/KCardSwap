"""
Upload Card Use Case - Generate signed URL for card image upload
"""

from datetime import datetime, timedelta
from typing import Dict
from uuid import UUID

from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.repositories.card_repository import CardRepository
from app.modules.social.domain.services.card_validation_service import (
    CardValidationService,
)
from app.modules.social.domain.value_objects.upload_quota import (
    QuotaExceeded,
    UploadQuota,
)


class UploadCardResult:
    """Result of upload card use case"""

    def __init__(
        self,
        upload_url: str,
        method: str,
        required_headers: Dict[str, str],
        image_url: str,
        expires_at: datetime,
        card_id: UUID,
    ):
        self.upload_url = upload_url
        self.method = method
        self.required_headers = required_headers
        self.image_url = image_url
        self.expires_at = expires_at
        self.card_id = card_id


class UploadCardUseCase:
    """
    Use case for initiating card image upload.
    Validates quota, generates signed URL, and creates card record.
    """

    def __init__(
        self,
        card_repository: CardRepository,
        validation_service: CardValidationService,
        gcs_service,  # GCSStorageService or MockGCSStorageService
    ):
        self.card_repository = card_repository
        self.validation_service = validation_service
        self.gcs_service = gcs_service

    async def execute(
        self,
        owner_id: UUID,
        content_type: str,
        file_size_bytes: int,
        quota: UploadQuota,
        idol: str = None,
        idol_group: str = None,
        album: str = None,
        version: str = None,
        rarity: str = None,
    ) -> UploadCardResult:
        """
        Generate signed URL for uploading a card image.

        Args:
            owner_id: ID of the card owner
            content_type: MIME type of the file
            file_size_bytes: Size of file in bytes
            quota: Upload quota for the user
            idol: Idol name (optional)
            idol_group: Idol group (optional)
            album: Album name (optional)
            version: Version (optional)
            rarity: Card rarity (optional)

        Returns:
            UploadCardResult with signed URL and card info

        Raises:
            QuotaExceeded: If any quota limit is exceeded
            ValueError: If validation fails
        """
        # Validate content type and file size
        is_valid, error_message = self.validation_service.validate_upload_request(
            content_type, file_size_bytes, quota.max_file_size_bytes
        )
        if not is_valid:
            raise ValueError(error_message)

        # Check daily upload limit
        uploads_today = await self.card_repository.count_uploads_today(owner_id)
        if not quota.can_upload_today(uploads_today):
            raise QuotaExceeded(
                f"Daily upload limit of {quota.daily_limit} reached",
                limit_type="daily",
            )

        # Check total storage limit
        current_storage = await self.card_repository.get_total_storage_used(owner_id)
        if not quota.has_storage_space(current_storage, file_size_bytes):
            total_gb = quota.total_storage_bytes / (1024 * 1024 * 1024)
            raise QuotaExceeded(
                f"Total storage limit of {total_gb:.1f}GB exceeded",
                limit_type="storage",
            )

        # Create card record (without image URL yet)
        card = Card(
            owner_id=owner_id,
            idol=idol,
            idol_group=idol_group,
            album=album,
            version=version,
            rarity=rarity,
            status=Card.STATUS_AVAILABLE,
            size_bytes=file_size_bytes,
        )

        # Save card to get ID
        saved_card = await self.card_repository.save(card)

        # Generate GCS blob path: cards/{user_id}/{card_id}{ext}
        file_extension = self.validation_service.get_file_extension(content_type)
        blob_name = f"cards/{owner_id}/{saved_card.id}{file_extension}"

        # Generate signed URL (15 minutes expiration)
        expiration_minutes = 15
        upload_url = self.gcs_service.generate_upload_signed_url(
            blob_name=blob_name,
            content_type=content_type,
            expiration_minutes=expiration_minutes,
        )

        # Build public image URL (without query params)
        bucket_name = getattr(self.gcs_service, "_bucket_name", "kcardswap")
        image_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

        # Update card with image URL
        saved_card.update_image(image_url, file_size_bytes)
        await self.card_repository.save(saved_card)

        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=expiration_minutes)

        return UploadCardResult(
            upload_url=upload_url,
            method="PUT",
            required_headers={"Content-Type": content_type},
            image_url=image_url,
            expires_at=expires_at,
            card_id=saved_card.id,
        )
