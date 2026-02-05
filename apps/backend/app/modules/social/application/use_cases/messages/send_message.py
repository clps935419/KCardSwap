"""Send Message in Thread Use Case"""

import uuid
from datetime import datetime
from typing import Optional

from app.modules.social.domain.entities.thread_message import ThreadMessage
from app.modules.social.domain.repositories.i_thread_message_repository import (
    IThreadMessageRepository,
)
from app.modules.social.domain.repositories.i_thread_repository import IThreadRepository


class SendMessageUseCase:
    """
    Use case for sending a message in a thread.

    Supports FR-015: Messages can reference post_id.
    """

    def __init__(
        self,
        thread_repository: IThreadRepository,
        thread_message_repository: IThreadMessageRepository,
    ):
        self.thread_repository = thread_repository
        self.thread_message_repository = thread_message_repository

    async def execute(
        self,
        thread_id: str,
        sender_id: str,
        content: str,
        post_id: Optional[str] = None,
    ) -> ThreadMessage:
        """
        Send a message in a thread.

        Args:
            thread_id: ID of the thread
            sender_id: ID of the user sending the message
            content: Message content
            post_id: Optional post ID to reference

        Returns:
            Created ThreadMessage entity

        Raises:
            ValueError: If thread not found or user not authorized
        """
        # Verify thread exists
        thread = await self.thread_repository.get_by_id(thread_id)
        if not thread:
            raise ValueError("Thread not found")

        # Verify sender is part of thread
        if not thread.has_user(sender_id):
            raise ValueError("You are not authorized to send messages in this thread")

        # Create message
        message = ThreadMessage(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            sender_id=sender_id,
            content=content,
            post_id=post_id,
            created_at=datetime.utcnow(),
        )
        created_message = await self.thread_message_repository.create(message)

        # Update thread's last_message_at
        thread.update_last_message_time(created_message.created_at)
        await self.thread_repository.update(thread)

        return created_message
