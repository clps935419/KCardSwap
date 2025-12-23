"""
Expire Subscriptions Use Case - For periodic background tasks
"""
import logging
from datetime import datetime

from app.modules.identity.domain.repositories.subscription_repository import SubscriptionRepository

logger = logging.getLogger(__name__)


class ExpireSubscriptionsUseCase:
    """
    Use case for expiring subscriptions.
    Should be run as a daily background task.
    """
    
    def __init__(self, subscription_repository: SubscriptionRepository):
        self.subscription_repo = subscription_repository
    
    async def execute(self) -> dict:
        """
        Expire all active subscriptions that have passed their expiry date.
        
        Returns:
            dict with:
            - expired_count: Number of subscriptions expired
            - processed_at: Timestamp of processing
        """
        now = datetime.utcnow()
        
        # Get all expired subscriptions
        expired_subscriptions = await self.subscription_repo.get_expired_subscriptions(before=now)
        
        # Mark each as expired
        expired_count = 0
        for subscription in expired_subscriptions:
            subscription.mark_as_expired()
            await self.subscription_repo.update(subscription)
            expired_count += 1
            logger.info(f"Expired subscription for user_id={subscription.user_id}")
        
        result = {
            "expired_count": expired_count,
            "processed_at": now.isoformat(),
        }
        
        logger.info(f"Subscription expiry job completed: {result}")
        return result
