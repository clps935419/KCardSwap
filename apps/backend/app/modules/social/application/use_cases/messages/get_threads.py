"""Get Threads for User Use Case"""

from typing import List

from app.modules.social.domain.entities.thread import MessageThread
from app.modules.social.domain.repositories.i_thread_repository import IThreadRepository


class GetThreadsUseCase:
    """
    Use case for getting all threads for a user.

    Supports FR-016: Inbox clearly separates Requests vs Threads.
    """

    def __init__(
        self,
        thread_repository: IThreadRepository,
    ):
        self.thread_repository = thread_repository

    async def execute(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[MessageThread]:
        """
        Get all threads for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of threads to return
            offset: Pagination offset

        Returns:
            List of MessageThread entities ordered by last_message_at descending
        """
        return await self.thread_repository.get_threads_for_user(
            user_id, limit=limit, offset=offset
        )
