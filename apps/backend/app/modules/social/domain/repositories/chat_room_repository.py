"""
ChatRoom Repository Interface

Domain layer repository interface - defines contract for chat room persistence
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.social.domain.entities.chat_room import ChatRoom


class ChatRoomRepository(ABC):
    """Repository interface for ChatRoom entity persistence"""

    @abstractmethod
    async def create(self, chat_room: ChatRoom) -> ChatRoom:
        """Create a new chat room"""
        pass

    @abstractmethod
    async def get_by_id(self, room_id: str) -> Optional[ChatRoom]:
        """Get chat room by ID"""
        pass

    @abstractmethod
    async def get_by_participants(
        self, user_id_1: str, user_id_2: str
    ) -> Optional[ChatRoom]:
        """Get chat room by two participants (either order)"""
        pass

    @abstractmethod
    async def get_rooms_by_user_id(self, user_id: str) -> List[ChatRoom]:
        """Get all chat rooms for a user"""
        pass

    @abstractmethod
    async def delete(self, room_id: str) -> None:
        """Delete a chat room"""
        pass
