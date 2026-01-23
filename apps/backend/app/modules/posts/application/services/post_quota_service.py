"""Post Quota Service - Check posts_per_day quota.

This service implements quota checking for post creation according to POC spec FR-023.
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


class PostQuotaService:
    """Service for checking post-related quotas."""

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

    async def check_posts_per_day(
        self,
        user_id: UUID,
        current_count: int,
    ) -> None:
        """Check if user can create a post within daily quota.

        Args:
            user_id: User ID
            current_count: Current number of posts today

        Raises:
            LimitExceededException: If daily post limit exceeded
        """
        tier = await self._get_user_tier(user_id)
        limit = QUOTA_LIMITS[QuotaKey.POSTS_PER_DAY][tier]
        reset_at = get_next_reset_time(QuotaKey.POSTS_PER_DAY)

        if current_count >= limit:
            raise LimitExceededException(
                limit_key=QuotaKey.POSTS_PER_DAY.value,
                limit_value=limit,
                current_value=current_count,
                reset_at=reset_at,
                message=f"Daily post limit exceeded. {tier.value.capitalize()} users can create {limit} posts per day.",
            )

    async def get_post_images_limit(self, user_id: UUID) -> int:
        """Get the maximum number of images per post for user.

        Args:
            user_id: User ID

        Returns:
            Maximum images per post
        """
        tier = await self._get_user_tier(user_id)
        return QUOTA_LIMITS[QuotaKey.POST_IMAGES_PER_POST_MAX][tier]
