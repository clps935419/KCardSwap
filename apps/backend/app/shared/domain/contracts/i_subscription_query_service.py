"""
Subscription Query Service Interface

Contract for querying subscription status across bounded contexts.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID


class SubscriptionInfo:
    """DTO for subscription information"""

    def __init__(
        self,
        user_id: UUID,
        is_active: bool,
        expires_at: Optional[datetime] = None,
        plan_type: Optional[str] = None,
    ):
        self.user_id = user_id
        self.is_active = is_active
        self.expires_at = expires_at
        self.plan_type = plan_type


class ISubscriptionQueryService(ABC):
    """
    Interface for querying user subscription status.
    
    This service provides read-only access to subscription information
    without exposing the Identity bounded context's internal implementation.
    """

    @abstractmethod
    async def is_user_subscribed(self, user_id: UUID) -> bool:
        """
        Check if a user has an active subscription.
        
        Args:
            user_id: User UUID
            
        Returns:
            True if user has active subscription, False otherwise
        """
        pass

    @abstractmethod
    async def get_subscription_info(self, user_id: UUID) -> Optional[SubscriptionInfo]:
        """
        Get detailed subscription information for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            SubscriptionInfo if user has subscription, None otherwise
        """
        pass

    @abstractmethod
    async def get_or_create_subscription_info(self, user_id: UUID) -> SubscriptionInfo:
        """
        Get subscription information for a user, creating default subscription if not exists.
        
        This is used for ensuring every user has a subscription record (defaulting to free plan).
        
        Args:
            user_id: User UUID
            
        Returns:
            SubscriptionInfo (always returns a value, creating free plan if needed)
        """
        pass
