"""Quota Management Domain Interface.

This module defines the quota keys, limits, and service interface
for managing content and media quotas across the application.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Protocol

from app.shared.presentation.errors.limit_exceeded import LimitExceededException


class QuotaKey(str, Enum):
    """Quota limit keys as defined in POC spec."""

    # Posts quota
    POSTS_PER_DAY = "posts_per_day"
    POST_IMAGES_PER_POST_MAX = "post_images_per_post_max"

    # Gallery quota
    GALLERY_CARDS_COUNT_MAX = "gallery_cards_count_max"

    # Media quota
    MEDIA_FILE_BYTES_MAX = "media_file_bytes_max"
    MEDIA_BYTES_PER_MONTH = "media_bytes_per_month"


class SubscriptionTier(str, Enum):
    """Subscription tiers."""

    FREE = "free"
    PREMIUM = "premium"


# Default quota values as per spec (FR-023)
QUOTA_LIMITS = {
    QuotaKey.POSTS_PER_DAY: {
        SubscriptionTier.FREE: 2,
        SubscriptionTier.PREMIUM: 20,
    },
    QuotaKey.POST_IMAGES_PER_POST_MAX: {
        SubscriptionTier.FREE: 1,
        SubscriptionTier.PREMIUM: 4,
    },
    QuotaKey.GALLERY_CARDS_COUNT_MAX: {
        SubscriptionTier.FREE: 50,
        SubscriptionTier.PREMIUM: 500,
    },
    QuotaKey.MEDIA_FILE_BYTES_MAX: {
        SubscriptionTier.FREE: 1 * 1024 * 1024,  # 1MB
        SubscriptionTier.PREMIUM: 5 * 1024 * 1024,  # 5MB
    },
    QuotaKey.MEDIA_BYTES_PER_MONTH: {
        SubscriptionTier.FREE: 50 * 1024 * 1024,  # 50MB
        SubscriptionTier.PREMIUM: 2 * 1024 * 1024 * 1024,  # 2GB
    },
}


class QuotaService(Protocol):
    """Protocol for quota checking services.

    Implementations should:
    1. Check current usage against limits
    2. Raise LimitExceededException if exceeded
    3. Provide reset_at datetime for periodic limits
    """

    async def check_quota(
        self,
        user_id: str,
        quota_key: QuotaKey,
        increment: int | float = 1,
    ) -> None:
        """Check if user can perform action within quota.

        Args:
            user_id: User ID to check quota for
            quota_key: Which quota to check
            increment: How much to increment (default 1 for count-based)

        Raises:
            LimitExceededException: If quota would be exceeded
        """
        ...

    async def get_current_usage(
        self,
        user_id: str,
        quota_key: QuotaKey,
    ) -> int | float:
        """Get current usage for a quota.

        Args:
            user_id: User ID
            quota_key: Which quota to check

        Returns:
            Current usage value
        """
        ...

    async def get_limit_value(
        self,
        user_id: str,
        quota_key: QuotaKey,
    ) -> int | float:
        """Get the limit value for a user and quota.

        Args:
            user_id: User ID
            quota_key: Which quota to check

        Returns:
            Limit value based on user's subscription tier
        """
        ...

    async def get_reset_time(
        self,
        quota_key: QuotaKey,
    ) -> datetime:
        """Get the reset time for a periodic quota.

        Args:
            quota_key: Which quota to check

        Returns:
            DateTime when the quota resets (UTC)
        """
        ...


def get_next_reset_time(quota_key: QuotaKey) -> datetime:
    """Calculate next reset time for a quota key.

    Args:
        quota_key: Quota to calculate reset time for

    Returns:
        Next reset datetime (UTC, timezone-aware)

    Notes:
        - POSTS_PER_DAY resets at 00:00 Asia/Taipei (16:00 UTC previous day)
        - MEDIA_BYTES_PER_MONTH resets at 1st of month 00:00 Asia/Taipei
        - Other quotas don't have periodic resets (return far future)
    """
    from zoneinfo import ZoneInfo

    taipei_tz = ZoneInfo("Asia/Taipei")
    now_taipei = datetime.now(taipei_tz)

    if quota_key == QuotaKey.POSTS_PER_DAY:
        # Next midnight in Taipei
        next_midnight_taipei = (now_taipei + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return next_midnight_taipei.astimezone(ZoneInfo("UTC"))

    elif quota_key == QuotaKey.MEDIA_BYTES_PER_MONTH:
        # Next 1st of month at midnight in Taipei
        if now_taipei.day == 1 and now_taipei.hour == 0 and now_taipei.minute == 0:
            # If exactly at reset time, use next month
            next_month = now_taipei + timedelta(days=32)
        else:
            next_month = now_taipei + timedelta(days=32)

        next_reset_taipei = next_month.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return next_reset_taipei.astimezone(ZoneInfo("UTC"))

    else:
        # No periodic reset (total/max limits)
        return datetime.max.replace(tzinfo=ZoneInfo("UTC"))
