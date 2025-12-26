"""
SQLAlchemy Message Repository Implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.message import Message, MessageStatus
from app.modules.social.domain.repositories.i_message_repository import IMessageRepository
from app.modules.social.infrastructure.database.models.message_model import MessageModel


class MessageRepositoryImpl(IMessageRepository):
    """SQLAlchemy implementation of Message repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message: Message) -> Message:
        """Create a new message"""
        model = MessageModel(
            id=UUID(message.id) if isinstance(message.id, str) else message.id,
            room_id=UUID(message.room_id) if isinstance(message.room_id, str) else message.room_id,
            sender_id=UUID(message.sender_id) if isinstance(message.sender_id, str) else message.sender_id,
            content=message.content,
            status=message.status.value if isinstance(message.status, MessageStatus) else message.status,
            created_at=message.created_at,
            updated_at=message.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID"""
        result = await self.session.execute(
            select(MessageModel).where(MessageModel.id == UUID(message_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_messages_by_room_id(
        self,
        room_id: str,
        after_message_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Message]:
        """
        Get messages for a chat room

        Supports incremental polling using after_message_id cursor.
        Returns messages newer than after_message_id, ordered by created_at ASC.

        Args:
            room_id: Chat room ID
            after_message_id: Optional cursor - return messages with ID > this
            limit: Maximum number of messages to return

        Returns:
            List of messages ordered by created_at ascending
        """
        room_uuid = UUID(room_id) if isinstance(room_id, str) else room_id

        query = select(MessageModel).where(MessageModel.room_id == room_uuid)

        # Apply cursor-based pagination if after_message_id is provided
        if after_message_id:
            after_uuid = UUID(after_message_id) if isinstance(after_message_id, str) else after_message_id
            query = query.where(MessageModel.id > after_uuid)

        # Order by created_at ASC for incremental polling
        query = query.order_by(MessageModel.created_at.asc()).limit(limit)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, message: Message) -> Message:
        """Update an existing message (e.g., delivery status)"""
        result = await self.session.execute(
            select(MessageModel).where(
                MessageModel.id == (UUID(message.id) if isinstance(message.id, str) else message.id)
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Message with id {message.id} not found")

        model.content = message.content
        model.status = message.status.value if isinstance(message.status, MessageStatus) else message.status
        model.updated_at = message.updated_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, message_id: str) -> None:
        """Delete a message"""
        result = await self.session.execute(
            select(MessageModel).where(MessageModel.id == UUID(message_id))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def get_unread_count_by_room_id(self, room_id: str, user_id: str) -> int:
        """Get count of unread messages in a room for a user"""
        room_uuid = UUID(room_id) if isinstance(room_id, str) else room_id
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        # Count messages that are not sent by user and not read
        result = await self.session.execute(
            select(func.count(MessageModel.id)).where(
                and_(
                    MessageModel.room_id == room_uuid,
                    MessageModel.sender_id != user_uuid,
                    MessageModel.status != MessageStatus.READ.value
                )
            )
        )
        count = result.scalar_one()
        return count or 0

    async def mark_messages_as_read(self, room_id: str, user_id: str) -> int:
        """
        Mark all messages in a room as read for a user

        Returns:
            Number of messages marked as read
        """
        room_uuid = UUID(room_id) if isinstance(room_id, str) else room_id
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        # Find all unread messages not sent by user
        result = await self.session.execute(
            select(MessageModel).where(
                and_(
                    MessageModel.room_id == room_uuid,
                    MessageModel.sender_id != user_uuid,
                    MessageModel.status != MessageStatus.READ.value
                )
            )
        )
        models = result.scalars().all()

        # Mark them as read
        count = 0
        for model in models:
            model.status = MessageStatus.READ.value
            count += 1

        if count > 0:
            await self.session.flush()

        return count

    @staticmethod
    def _to_entity(model: MessageModel) -> Message:
        """Convert ORM model to domain entity"""
        return Message(
            id=str(model.id),
            room_id=str(model.room_id),
            sender_id=str(model.sender_id),
            content=model.content,
            status=MessageStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Alias for consistency
MessageRepositoryImpl = MessageRepositoryImpl
