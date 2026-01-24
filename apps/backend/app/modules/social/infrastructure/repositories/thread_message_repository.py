"""ThreadMessage Repository Implementation"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.thread_message import ThreadMessage
from app.modules.social.domain.repositories.i_thread_message_repository import (
    IThreadMessageRepository,
)
from app.modules.social.infrastructure.database.models.thread_message_model import (
    ThreadMessageModel,
)


class ThreadMessageRepository(IThreadMessageRepository):
    """Repository implementation for ThreadMessage using SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ThreadMessageModel) -> ThreadMessage:
        """Convert ORM model to domain entity"""
        return ThreadMessage(
            id=str(model.id),
            thread_id=str(model.thread_id),
            sender_id=str(model.sender_id),
            content=model.content,
            post_id=str(model.post_id) if model.post_id else None,
            created_at=model.created_at,
        )

    def _to_model(self, entity: ThreadMessage) -> ThreadMessageModel:
        """Convert domain entity to ORM model"""
        return ThreadMessageModel(
            id=UUID(entity.id),
            thread_id=UUID(entity.thread_id),
            sender_id=UUID(entity.sender_id),
            content=entity.content,
            post_id=UUID(entity.post_id) if entity.post_id else None,
            created_at=entity.created_at,
        )

    async def create(self, message: ThreadMessage) -> ThreadMessage:
        """Create a new message in a thread"""
        model = self._to_model(message)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, message_id: str) -> Optional[ThreadMessage]:
        """Get message by ID"""
        stmt = select(ThreadMessageModel).where(
            ThreadMessageModel.id == UUID(message_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_messages_by_thread(
        self, thread_id: str, limit: int = 50, offset: int = 0
    ) -> List[ThreadMessage]:
        """Get messages for a thread (ordered by created_at ascending)"""
        stmt = (
            select(ThreadMessageModel)
            .where(ThreadMessageModel.thread_id == UUID(thread_id))
            .order_by(ThreadMessageModel.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def delete(self, message_id: str) -> None:
        """Delete a message"""
        stmt = select(ThreadMessageModel).where(
            ThreadMessageModel.id == UUID(message_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        await self.session.delete(model)
        await self.session.flush()

    async def get_thread_message_count(self, thread_id: str) -> int:
        """Get total message count in a thread"""
        stmt = select(func.count()).where(
            ThreadMessageModel.thread_id == UUID(thread_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
