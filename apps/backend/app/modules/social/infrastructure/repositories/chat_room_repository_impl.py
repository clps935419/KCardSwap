"""
SQLAlchemy ChatRoom Repository Implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, any_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.repositories.i_chat_room_repository import (
    IChatRoomRepository,
)
from app.modules.social.infrastructure.database.models.chat_room_model import (
    ChatRoomModel,
)


class ChatRoomRepositoryImpl(IChatRoomRepository):
    """SQLAlchemy implementation of ChatRoom repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, chat_room: ChatRoom) -> ChatRoom:
        """Create a new chat room"""
        # Convert participant IDs to UUIDs and sort them
        participant_uuids = sorted(
            [
                UUID(pid) if isinstance(pid, str) else pid
                for pid in chat_room.participant_ids
            ]
        )

        model = ChatRoomModel(
            id=UUID(chat_room.id) if isinstance(chat_room.id, str) else chat_room.id,
            participant_ids=participant_uuids,
            created_at=chat_room.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, room_id: str) -> Optional[ChatRoom]:
        """Get chat room by ID"""
        result = await self.session.execute(
            select(ChatRoomModel).where(ChatRoomModel.id == UUID(room_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_participants(
        self, user_id_1: str, user_id_2: str
    ) -> Optional[ChatRoom]:
        """Get chat room by two participants (either order)"""
        # Convert to UUIDs and sort to match storage format
        participant_uuids = sorted(
            [
                UUID(user_id_1) if isinstance(user_id_1, str) else user_id_1,
                UUID(user_id_2) if isinstance(user_id_2, str) else user_id_2,
            ]
        )

        # Query for exact match of sorted participant array
        result = await self.session.execute(
            select(ChatRoomModel).where(
                ChatRoomModel.participant_ids == participant_uuids
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_rooms_by_user_id(self, user_id: str) -> List[ChatRoom]:
        """Get all chat rooms for a user"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        # Use ANY operator to find rooms where user is a participant in the array
        result = await self.session.execute(
            select(ChatRoomModel)
            .where(user_uuid == any_(ChatRoomModel.participant_ids))
            .order_by(ChatRoomModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def delete(self, room_id: str) -> None:
        """Delete a chat room"""
        result = await self.session.execute(
            select(ChatRoomModel).where(ChatRoomModel.id == UUID(room_id))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    @staticmethod
    def _to_entity(model: ChatRoomModel) -> ChatRoom:
        """Convert ORM model to domain entity"""
        return ChatRoom(
            id=str(model.id),
            participant_ids=[str(pid) for pid in model.participant_ids],
            created_at=model.created_at,
        )


# Alias for consistency
ChatRoomRepositoryImpl = ChatRoomRepositoryImpl
