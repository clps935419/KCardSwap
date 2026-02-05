"""Get Messages in Thread Use Case"""

from typing import List

from app.modules.social.domain.entities.thread_message import ThreadMessage
from app.modules.social.domain.repositories.i_thread_message_repository import (
    IThreadMessageRepository,
)
from app.modules.social.domain.repositories.i_thread_repository import IThreadRepository


class GetThreadMessagesUseCase:
    """
    Use case for getting messages in a thread.
    """

    def __init__(
        self,
        thread_repository: IThreadRepository,
        thread_message_repository: IThreadMessageRepository,
    ):
        self.thread_repository = thread_repository
        self.thread_message_repository = thread_message_repository

    async def execute(
        self, thread_id: str, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[ThreadMessage]:
        """
        Get messages in a thread.

        Args:
            thread_id: ID of the thread
            user_id: ID of the requesting user (must be part of thread)
            limit: Maximum number of messages to return
            offset: Pagination offset

        Returns:
            List of ThreadMessage entities ordered by created_at ascending

        Raises:
            ValueError: If thread not found or user not authorized
        """
        # Verify thread exists
        thread = await self.thread_repository.get_by_id(thread_id)
        if not thread:
            raise ValueError("Thread not found")

        # Verify user is part of thread
        if not thread.has_user(user_id):
            raise ValueError("You are not authorized to view this thread")

        return await self.thread_message_repository.get_messages_by_thread(
            thread_id, limit=limit, offset=offset
        )
