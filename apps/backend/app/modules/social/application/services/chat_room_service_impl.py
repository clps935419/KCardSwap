"""
Chat Room Service Implementation

Implements IChatRoomService from shared contracts.
"""

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.repositories.i_chat_room_repository import (
    IChatRoomRepository,
)
from app.shared.domain.contracts.i_chat_room_service import (
    ChatRoomDTO,
    IChatRoomService,
)


class ChatRoomServiceImpl(IChatRoomService):
    """
    Implementation of chat room service.

    Provides chat room management functionality for other bounded contexts.
    """

    def __init__(self, chat_room_repository: IChatRoomRepository):
        self.chat_room_repository = chat_room_repository

    def _to_dto(self, chat_room: ChatRoom) -> ChatRoomDTO:
        """Convert domain entity to DTO."""
        # ChatRoom stores participant_ids as sorted list of 2 elements
        return ChatRoomDTO(
            id=UUID(chat_room.id),
            participant1_id=UUID(chat_room.participant_ids[0]),
            participant2_id=UUID(chat_room.participant_ids[1]),
        )

    async def get_or_create_chat_room(
        self, user1_id: UUID, user2_id: UUID
    ) -> ChatRoomDTO:
        """Get existing chat room or create a new one for two users."""
        # Try to find existing chat room
        existing = await self.chat_room_repository.get_by_participants(
            str(user1_id), str(user2_id)
        )
        if existing:
            return self._to_dto(existing)

        # Create new chat room
        chat_room = ChatRoom(
            id=str(uuid.uuid4()),
            participant_ids=[str(user1_id), str(user2_id)],
            created_at=datetime.utcnow(),
        )

        created = await self.chat_room_repository.create(chat_room)
        return self._to_dto(created)

    async def get_chat_room_between_users(
        self, user1_id: UUID, user2_id: UUID
    ) -> Optional[ChatRoomDTO]:
        """Get chat room between two users if it exists."""
        chat_room = await self.chat_room_repository.get_by_participants(
            str(user1_id), str(user2_id)
        )
        if not chat_room:
            return None
        return self._to_dto(chat_room)
