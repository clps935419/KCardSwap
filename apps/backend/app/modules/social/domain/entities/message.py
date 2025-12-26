"""
Message Entity - Represents a chat message in a room

Domain Entity following DDD principles - framework independent
"""

from datetime import datetime
from enum import Enum
from typing import Optional


class MessageStatus(str, Enum):
    """Message delivery status enumeration"""

    SENT = "sent"  # Message sent to server
    DELIVERED = "delivered"  # Message delivered to recipient device
    READ = "read"  # Message read by recipient


class Message:
    """
    Message Entity

    Represents a single message in a chat room.
    Tracks delivery status and supports polling with after_message_id cursor.

    Note: Messages are retained for 30 days on the server (FR-CHAT-006).
    Cleanup implementation is deferred (T125A).
    """

    def __init__(
        self,
        id: str,
        room_id: str,
        sender_id: str,
        content: str,
        status: MessageStatus,
        created_at: datetime,
        updated_at: Optional[datetime] = None,
    ):
        if not content or len(content.strip()) == 0:
            raise ValueError("Message content cannot be empty")

        # Maximum message length validation (prevent spam/abuse)
        if len(content) > 5000:
            raise ValueError(
                "Message content exceeds maximum length of 5000 characters"
            )

        self.id = id
        self.room_id = room_id
        self.sender_id = sender_id
        self.content = content
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at or created_at

    def mark_delivered(self) -> None:
        """Mark message as delivered to recipient device"""
        if self.status == MessageStatus.SENT:
            self.status = MessageStatus.DELIVERED
            self.updated_at = datetime.utcnow()

    def mark_read(self) -> None:
        """Mark message as read by recipient"""
        if self.status in (MessageStatus.SENT, MessageStatus.DELIVERED):
            self.status = MessageStatus.READ
            self.updated_at = datetime.utcnow()

    def is_sent_by(self, user_id: str) -> bool:
        """Check if message was sent by given user"""
        return self.sender_id == user_id

    def __repr__(self) -> str:
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return (
            f"Message(id={self.id}, room_id={self.room_id}, "
            f"sender_id={self.sender_id}, status={self.status}, "
            f"content='{content_preview}')"
        )
