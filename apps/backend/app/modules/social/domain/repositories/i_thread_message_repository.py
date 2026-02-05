"""
ThreadMessage Repository Interface

Domain layer repository interface - defines contract for thread message persistence
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.social.domain.entities.thread_message import ThreadMessage


class IThreadMessageRepository(ABC):
    """Repository interface for ThreadMessage entity persistence"""

    @abstractmethod
    async def create(self, message: ThreadMessage) -> ThreadMessage:
        """Create a new message in a thread"""
        pass

    @abstractmethod
    async def get_by_id(self, message_id: str) -> Optional[ThreadMessage]:
        """Get message by ID"""
        pass

    @abstractmethod
    async def get_messages_by_thread(
        self, thread_id: str, limit: int = 50, offset: int = 0
    ) -> List[ThreadMessage]:
        """
        Get messages for a thread

        Args:
            thread_id: Thread ID
            limit: Maximum number of messages to return
            offset: Pagination offset

        Returns:
            List of messages ordered by created_at ascending (oldest first)
        """
        pass

    @abstractmethod
    async def delete(self, message_id: str) -> None:
        """Delete a message"""
        pass

    @abstractmethod
    async def get_thread_message_count(self, thread_id: str) -> int:
        """Get total message count in a thread"""
        pass
