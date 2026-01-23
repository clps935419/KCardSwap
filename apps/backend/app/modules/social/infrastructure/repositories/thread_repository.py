"""Thread Repository Implementation"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.thread import MessageThread
from app.modules.social.domain.repositories.i_thread_repository import IThreadRepository
from app.modules.social.infrastructure.database.models.thread_model import (
    MessageThreadModel,
)


class ThreadRepository(IThreadRepository):
    """Repository implementation for MessageThread using SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: MessageThreadModel) -> MessageThread:
        """Convert ORM model to domain entity"""
        return MessageThread(
            id=str(model.id),
            user_a_id=str(model.user_a_id),
            user_b_id=str(model.user_b_id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_message_at=model.last_message_at,
        )

    def _to_model(self, entity: MessageThread) -> MessageThreadModel:
        """Convert domain entity to ORM model"""
        return MessageThreadModel(
            id=UUID(entity.id),
            user_a_id=UUID(entity.user_a_id),
            user_b_id=UUID(entity.user_b_id),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_message_at=entity.last_message_at,
        )

    async def create(self, thread: MessageThread) -> MessageThread:
        """Create a new message thread"""
        model = self._to_model(thread)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, thread_id: str) -> Optional[MessageThread]:
        """Get thread by ID"""
        stmt = select(MessageThreadModel).where(MessageThreadModel.id == UUID(thread_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_users(
        self, user_a_id: str, user_b_id: str
    ) -> Optional[MessageThread]:
        """Find thread between two users (order-independent)"""
        # Normalize user order (smaller UUID first)
        if user_a_id > user_b_id:
            user_a_id, user_b_id = user_b_id, user_a_id

        stmt = select(MessageThreadModel).where(
            MessageThreadModel.user_a_id == UUID(user_a_id),
            MessageThreadModel.user_b_id == UUID(user_b_id),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_threads_for_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[MessageThread]:
        """Get all threads for a user"""
        stmt = (
            select(MessageThreadModel)
            .where(
                or_(
                    MessageThreadModel.user_a_id == UUID(user_id),
                    MessageThreadModel.user_b_id == UUID(user_id),
                )
            )
            .order_by(MessageThreadModel.last_message_at.desc().nullslast())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, thread: MessageThread) -> MessageThread:
        """Update an existing thread"""
        stmt = select(MessageThreadModel).where(
            MessageThreadModel.id == UUID(thread.id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one()

        model.updated_at = thread.updated_at
        model.last_message_at = thread.last_message_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, thread_id: str) -> None:
        """Delete a thread"""
        stmt = select(MessageThreadModel).where(
            MessageThreadModel.id == UUID(thread_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        await self.session.delete(model)
        await self.session.flush()
