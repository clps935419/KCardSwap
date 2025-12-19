"""
Check Upload Quota Use Case - Check user's upload quota status
"""

from typing import Dict
from uuid import UUID

from app.modules.social.domain.repositories.card_repository import CardRepository
from app.modules.social.domain.value_objects.upload_quota import UploadQuota


class QuotaStatus:
    """Represents current quota usage status"""

    def __init__(
        self,
        uploads_today: int,
        daily_limit: int,
        remaining_uploads: int,
        storage_used_bytes: int,
        storage_limit_bytes: int,
        remaining_storage_bytes: int,
    ):
        self.uploads_today = uploads_today
        self.daily_limit = daily_limit
        self.remaining_uploads = remaining_uploads
        self.storage_used_bytes = storage_used_bytes
        self.storage_limit_bytes = storage_limit_bytes
        self.remaining_storage_bytes = remaining_storage_bytes

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "uploads_today": self.uploads_today,
            "daily_limit": self.daily_limit,
            "remaining_uploads": self.remaining_uploads,
            "storage_used_bytes": self.storage_used_bytes,
            "storage_limit_bytes": self.storage_limit_bytes,
            "remaining_storage_bytes": self.remaining_storage_bytes,
            "storage_used_mb": round(self.storage_used_bytes / (1024 * 1024), 2),
            "storage_limit_mb": round(self.storage_limit_bytes / (1024 * 1024), 2),
            "remaining_storage_mb": round(
                self.remaining_storage_bytes / (1024 * 1024), 2
            ),
        }


class CheckUploadQuotaUseCase:
    """Use case for checking user's upload quota"""

    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    async def execute(self, owner_id: UUID, quota: UploadQuota) -> QuotaStatus:
        """
        Check current quota usage for a user.

        Args:
            owner_id: Owner's user ID
            quota: Upload quota for the user

        Returns:
            QuotaStatus with current usage information
        """
        # Get uploads today
        uploads_today = await self.card_repository.count_uploads_today(owner_id)

        # Get storage usage
        storage_used = await self.card_repository.get_total_storage_used(owner_id)

        # Calculate remaining
        remaining_uploads = quota.get_remaining_uploads(uploads_today)
        remaining_storage = quota.get_remaining_storage_bytes(storage_used)

        return QuotaStatus(
            uploads_today=uploads_today,
            daily_limit=quota.daily_limit,
            remaining_uploads=remaining_uploads,
            storage_used_bytes=storage_used,
            storage_limit_bytes=quota.total_storage_bytes,
            remaining_storage_bytes=remaining_storage,
        )
