"""
Message Repository Interface

Domain layer repository interface - defines contract for message persistence
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.social.domain.entities.message import Message


class MessageRepository(ABC):
    """Repository interface for Message entity persistence"""

    @abstractmethod
    async def create(self, message: Message) -> Message:
        """Create a new message"""
        pass

    @abstractmethod
    async def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID"""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def update(self, message: Message) -> Message:
        """Update an existing message (e.g., delivery status)"""
        pass

    @abstractmethod
    async def delete(self, message_id: str) -> None:
        """Delete a message"""
        pass

    @abstractmethod
    async def get_unread_count_by_room_id(self, room_id: str, user_id: str) -> int:
        """Get count of unread messages in a room for a user"""
        pass

    @abstractmethod
    async def mark_messages_as_read(self, room_id: str, user_id: str) -> int:
        """
        Mark all messages in a room as read for a user

        Returns:
            Number of messages marked as read
        """
        pass
