"""
Check Subscription Status Use Case
"""
from uuid import UUID

from app.modules.identity.domain.repositories.subscription_repository import (
    SubscriptionRepository,
)


class CheckSubscriptionStatusUseCase:
    """
    Use case for checking user's subscription status.
    Returns server-side subscription state.
    """

    def __init__(self, subscription_repository: SubscriptionRepository):
        self.subscription_repo = subscription_repository

    async def execute(self, user_id: UUID) -> dict:
        """
        Get current subscription status for user.

        Args:
            user_id: The user ID

        Returns:
            dict with:
            - plan: "free" or "premium"
            - status: "active", "inactive", "expired", "pending"
            - expires_at: datetime or None
            - entitlement_active: bool
            - source: "google_play"
        """
        # Get or create subscription (ensures every user has a subscription record)
        subscription = await self.subscription_repo.get_or_create_by_user_id(user_id)

        # Check if subscription should be expired
        if subscription.should_expire():
            subscription.mark_as_expired()
            subscription = await self.subscription_repo.update(subscription)

        entitlement_active = subscription.is_premium()

        return {
            "plan": subscription.plan,
            "status": subscription.status,
            "expires_at": subscription.expires_at.isoformat()
            if subscription.expires_at
            else None,
            "entitlement_active": entitlement_active,
            "source": "google_play",
        }
