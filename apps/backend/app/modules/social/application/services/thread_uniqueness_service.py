"""Thread Uniqueness Service - Ensures one thread per user pair (FR-014)"""

from typing import Optional

from app.modules.social.domain.entities.thread import MessageThread
from app.modules.social.domain.repositories.i_message_request_repository import (
    IMessageRequestRepository,
)
from app.modules.social.domain.repositories.i_thread_repository import IThreadRepository


class ThreadUniquenessService:
    """
    Service to enforce FR-014: One unique thread per user pair.
    
    Prevents duplicate threads and ensures proper routing to existing conversations.
    """

    def __init__(
        self,
        thread_repository: IThreadRepository,
        message_request_repository: IMessageRequestRepository,
    ):
        self.thread_repository = thread_repository
        self.message_request_repository = message_request_repository

    async def find_or_get_pending_request(
        self, user_a_id: str, user_b_id: str
    ) -> tuple[Optional[MessageThread], Optional[object]]:
        """
        Find existing thread or pending request between two users.
        
        Returns:
            tuple: (existing_thread, pending_request)
            - If thread exists: (Thread, None)
            - If pending request exists: (None, MessageRequest)
            - If neither: (None, None)
        """
        # Check for existing thread
        existing_thread = await self.thread_repository.find_by_users(user_a_id, user_b_id)
        if existing_thread:
            return (existing_thread, None)

        # Check for pending request
        pending_request = await self.message_request_repository.find_pending_between_users(
            user_a_id, user_b_id
        )
        if pending_request:
            return (None, pending_request)

        return (None, None)

    async def can_create_new_request(self, sender_id: str, recipient_id: str) -> bool:
        """
        Check if a new message request can be created.
        
        Returns:
            True if no thread or pending request exists, False otherwise.
        """
        existing_thread, pending_request = await self.find_or_get_pending_request(
            sender_id, recipient_id
        )
        return existing_thread is None and pending_request is None

    async def get_or_fail(self, user_a_id: str, user_b_id: str) -> MessageThread:
        """
        Get existing thread or raise error if not found.
        
        Used when sending messages - thread must already exist.
        
        Raises:
            ValueError: If thread does not exist
        """
        thread = await self.thread_repository.find_by_users(user_a_id, user_b_id)
        if not thread:
            raise ValueError(
                "No thread exists between these users. "
                "Message request must be accepted first."
            )
        return thread
