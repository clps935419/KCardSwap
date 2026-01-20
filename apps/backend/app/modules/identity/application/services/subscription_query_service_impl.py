"""
Subscription Query Service Implementation

Implements ISubscriptionQueryService from shared contracts.
"""

from typing import Optional
from uuid import UUID

from app.modules.identity.domain.repositories.i_subscription_repository import (
    ISubscriptionRepository,
)
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
    SubscriptionInfo,
)


class SubscriptionQueryServiceImpl(ISubscriptionQueryService):
    """
    Implementation of subscription query service.

    Provides read-only access to subscription information for other bounded contexts.
    """

    def __init__(self, subscription_repository: ISubscriptionRepository):
        self.subscription_repository = subscription_repository

    async def is_user_subscribed(self, user_id: UUID) -> bool:
        """Check if a user has an active subscription."""
        subscription = await self.subscription_repository.get_by_user_id(user_id)
        if not subscription:
            return False
        return subscription.is_active()

    async def get_subscription_info(self, user_id: UUID) -> Optional[SubscriptionInfo]:
        """Get detailed subscription information for a user."""
        subscription = await self.subscription_repository.get_by_user_id(user_id)
        if not subscription:
            return None

        return SubscriptionInfo(
            user_id=subscription.user_id,
            is_active=subscription.is_active(),
            expires_at=subscription.expires_at,
            plan_type=subscription.plan,
        )

    async def get_or_create_subscription_info(self, user_id: UUID) -> SubscriptionInfo:
        """Get subscription information for a user, creating default if not exists."""
        subscription = await self.subscription_repository.get_or_create_by_user_id(user_id)

        return SubscriptionInfo(
            user_id=subscription.user_id,
            is_active=subscription.is_active(),
            expires_at=subscription.expires_at,
            plan_type=subscription.plan,
        )
