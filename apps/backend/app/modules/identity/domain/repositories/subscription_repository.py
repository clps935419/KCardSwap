"""
Subscription Repository Interface
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from uuid import UUID

from ..entities.subscription import Subscription


class SubscriptionRepository(ABC):
    """Repository interface for Subscription entity"""

    @abstractmethod
    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription"""
        pass

    @abstractmethod
    async def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[Subscription]:
        """Get subscription by user ID"""
        pass

    @abstractmethod
    async def update(self, subscription: Subscription) -> Subscription:
        """Update existing subscription"""
        pass

    @abstractmethod
    async def get_expired_subscriptions(self, before: datetime) -> list[Subscription]:
        """Get all active subscriptions that have expired before given datetime"""
        pass

    @abstractmethod
    async def get_or_create_by_user_id(self, user_id: UUID) -> Subscription:
        """Get existing subscription or create a new free subscription for user"""
        pass
