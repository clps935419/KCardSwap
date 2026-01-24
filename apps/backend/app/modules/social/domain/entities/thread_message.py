"""
ThreadMessage Entity - Represents a message in a conversation thread

Domain Entity following DDD principles - framework independent
"""

from datetime import datetime
from typing import Optional


class ThreadMessage:
    """
    ThreadMessage Entity

    Represents a message sent in a MessageThread.
    Supports FR-015: Messages can reference post_id.
    """

    def __init__(
        self,
        id: str,
        thread_id: str,
        sender_id: str,
        content: str,
        post_id: Optional[str],
        created_at: datetime,
    ):
        if not content or len(content.strip()) == 0:
            raise ValueError("Message content cannot be empty")

        if len(content) > 5000:
            raise ValueError(
                "Message content exceeds maximum length of 5000 characters"
            )

        self.id = id
        self.thread_id = thread_id
        self.sender_id = sender_id
        self.content = content
        self.post_id = post_id
        self.created_at = created_at

    def is_sent_by(self, user_id: str) -> bool:
        """Check if message was sent by given user"""
        return self.sender_id == user_id

    def has_post_reference(self) -> bool:
        """Check if message references a post"""
        return self.post_id is not None

    def __repr__(self) -> str:
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return (
            f"ThreadMessage(id={self.id}, thread_id={self.thread_id}, "
            f"sender_id={self.sender_id}, content='{content_preview}')"
        )
