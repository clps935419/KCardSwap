"""
Subscription Repository Implementation
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain.entities.subscription import Subscription
from app.modules.identity.domain.repositories.subscription_repository import (
    SubscriptionRepository,
)
from app.modules.identity.infrastructure.database.models.subscription_model import (
    SubscriptionModel,
)


class SubscriptionRepositoryImpl(SubscriptionRepository):
    """SQLAlchemy implementation of SubscriptionRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: SubscriptionModel) -> Subscription:
        """Convert SQLAlchemy model to domain entity"""
        return Subscription(
            id=model.id,
            user_id=model.user_id,
            plan=model.plan,
            status=model.status,
            expires_at=model.expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Subscription) -> SubscriptionModel:
        """Convert domain entity to SQLAlchemy model"""
        return SubscriptionModel(
            id=entity.id,
            user_id=entity.user_id,
            plan=entity.plan,
            status=entity.status,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription"""
        model = self._to_model(subscription)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        result = await self.session.execute(
            select(SubscriptionModel).where(SubscriptionModel.id == subscription_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> Optional[Subscription]:
        """Get subscription by user ID"""
        result = await self.session.execute(
            select(SubscriptionModel).where(SubscriptionModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, subscription: Subscription) -> Subscription:
        """Update existing subscription"""
        result = await self.session.execute(
            select(SubscriptionModel).where(SubscriptionModel.id == subscription.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Subscription with id {subscription.id} not found")

        model.plan = subscription.plan
        model.status = subscription.status
        model.expires_at = subscription.expires_at
        model.updated_at = subscription.updated_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_expired_subscriptions(self, before: datetime) -> list[Subscription]:
        """Get all active subscriptions that have expired before given datetime"""
        result = await self.session.execute(
            select(SubscriptionModel).where(
                SubscriptionModel.status == "active",
                SubscriptionModel.expires_at <= before
            )
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_or_create_by_user_id(self, user_id: UUID) -> Subscription:
        """Get existing subscription or create a new free subscription for user"""
        subscription = await self.get_by_user_id(user_id)

        if subscription is None:
            # Create new free subscription
            subscription = Subscription(
                id=None,
                user_id=user_id,
                plan="free",
                status="inactive",
                expires_at=None,
            )
            subscription = await self.create(subscription)

        return subscription
