"""Media Quota Service - Check media upload quotas.

This service implements quota checking for media uploads according to POC spec FR-023.
Supports:
- media_file_bytes_max: Maximum file size per upload
- media_bytes_per_month: Monthly total media bytes quota
"""

from datetime import datetime
from uuid import UUID

from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)
from app.shared.domain.quota.quota_service import (
    QUOTA_LIMITS,
    QuotaKey,
    SubscriptionTier,
    get_next_reset_time,
)
from app.shared.presentation.errors.limit_exceeded import LimitExceededException


class MediaQuotaService:
    """Service for checking media-related quotas.
    
    This service checks:
    1. Individual file size limit (media_file_bytes_max)
    2. Monthly total upload bytes limit (media_bytes_per_month)
    """

    def __init__(
        self,
        subscription_service: ISubscriptionQueryService,
    ):
        self.subscription_service = subscription_service

    async def _get_user_tier(self, user_id: UUID) -> SubscriptionTier:
        """Get user's subscription tier.

        Args:
            user_id: User ID

        Returns:
            SubscriptionTier (FREE or PREMIUM)
        """
        subscription_info = await self.subscription_service.get_subscription_info(
            user_id
        )
        is_premium = (
            subscription_info
            and subscription_info.is_active
            and subscription_info.plan_type == "premium"
        )
        return SubscriptionTier.PREMIUM if is_premium else SubscriptionTier.FREE

    async def check_file_size(
        self,
        user_id: UUID,
        file_size_bytes: int,
    ) -> None:
        """Check if file size is within user's limit.

        Args:
            user_id: User ID
            file_size_bytes: Size of the file in bytes

        Raises:
            LimitExceededException: If file size exceeds limit
        """
        tier = await self._get_user_tier(user_id)
        limit = QUOTA_LIMITS[QuotaKey.MEDIA_FILE_BYTES_MAX][tier]

        if file_size_bytes > limit:
            # No periodic reset for file size limit
            reset_at = datetime.max.replace(tzinfo=None)
            raise LimitExceededException(
                limit_key=QuotaKey.MEDIA_FILE_BYTES_MAX.value,
                limit_value=limit,
                current_value=file_size_bytes,
                reset_at=reset_at,
                message=f"File size exceeds limit. {tier.value.capitalize()} users can upload files up to {limit / (1024 * 1024):.1f}MB.",
            )

    async def check_monthly_bytes(
        self,
        user_id: UUID,
        current_bytes_used: int,
        additional_bytes: int,
    ) -> None:
        """Check if uploading additional bytes would exceed monthly quota.

        Args:
            user_id: User ID
            current_bytes_used: Bytes already used this month
            additional_bytes: Bytes to be added

        Raises:
            LimitExceededException: If monthly quota would be exceeded
        """
        tier = await self._get_user_tier(user_id)
        limit = QUOTA_LIMITS[QuotaKey.MEDIA_BYTES_PER_MONTH][tier]
        reset_at = get_next_reset_time(QuotaKey.MEDIA_BYTES_PER_MONTH)

        new_total = current_bytes_used + additional_bytes

        if new_total > limit:
            raise LimitExceededException(
                limit_key=QuotaKey.MEDIA_BYTES_PER_MONTH.value,
                limit_value=limit,
                current_value=current_bytes_used,
                reset_at=reset_at,
                message=f"Monthly media quota exceeded. {tier.value.capitalize()} users can upload {limit / (1024 * 1024):.0f}MB per month.",
            )

    async def get_file_size_limit(self, user_id: UUID) -> int:
        """Get the maximum file size limit for user.

        Args:
            user_id: User ID

        Returns:
            Maximum file size in bytes
        """
        tier = await self._get_user_tier(user_id)
        return QUOTA_LIMITS[QuotaKey.MEDIA_FILE_BYTES_MAX][tier]

    async def get_monthly_bytes_limit(self, user_id: UUID) -> int:
        """Get the monthly bytes limit for user.

        Args:
            user_id: User ID

        Returns:
            Monthly bytes limit
        """
        tier = await self._get_user_tier(user_id)
        return QUOTA_LIMITS[QuotaKey.MEDIA_BYTES_PER_MONTH][tier]
