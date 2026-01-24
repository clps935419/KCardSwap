"""
MessageThread Repository Interface

Domain layer repository interface - defines contract for thread persistence
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.social.domain.entities.thread import MessageThread


class IThreadRepository(ABC):
    """Repository interface for MessageThread entity persistence"""

    @abstractmethod
    async def create(self, thread: MessageThread) -> MessageThread:
        """Create a new message thread"""
        pass

    @abstractmethod
    async def get_by_id(self, thread_id: str) -> Optional[MessageThread]:
        """Get thread by ID"""
        pass

    @abstractmethod
    async def find_by_users(
        self, user_a_id: str, user_b_id: str
    ) -> Optional[MessageThread]:
        """
        Find thread between two users (order-independent)
        
        Returns the unique thread if exists, None otherwise.
        This supports FR-014: One unique thread per user pair.
        """
        pass

    @abstractmethod
    async def get_threads_for_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[MessageThread]:
        """
        Get all threads for a user
        
        Args:
            user_id: ID of the user
            limit: Maximum number of threads to return
            offset: Pagination offset
        
        Returns:
            List of threads ordered by last_message_at descending
        """
        pass

    @abstractmethod
    async def update(self, thread: MessageThread) -> MessageThread:
        """Update an existing thread"""
        pass

    @abstractmethod
    async def delete(self, thread_id: str) -> None:
        """Delete a thread"""
        pass
