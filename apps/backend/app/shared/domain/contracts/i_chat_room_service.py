"""
Chat Room Service Interface

Contract for managing chat rooms across bounded contexts.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class ChatRoomDTO:
    """DTO for chat room information"""

    def __init__(self, id: UUID, participant1_id: UUID, participant2_id: UUID):
        self.id = id
        self.participant1_id = participant1_id
        self.participant2_id = participant2_id


class IChatRoomService(ABC):
    """
    Interface for managing chat rooms.
    
    This service provides chat room management functionality
    without exposing the Social bounded context's internal implementation.
    """

    @abstractmethod
    async def get_or_create_chat_room(
        self, user1_id: UUID, user2_id: UUID
    ) -> ChatRoomDTO:
        """
        Get existing chat room or create a new one for two users.
        
        Args:
            user1_id: First user UUID
            user2_id: Second user UUID
            
        Returns:
            ChatRoomDTO for the chat room
        """
        pass

    @abstractmethod
    async def get_chat_room_between_users(
        self, user1_id: UUID, user2_id: UUID
    ) -> Optional[ChatRoomDTO]:
        """
        Get chat room between two users if it exists.
        
        Args:
            user1_id: First user UUID
            user2_id: Second user UUID
            
        Returns:
            ChatRoomDTO if chat room exists, None otherwise
        """
        pass
