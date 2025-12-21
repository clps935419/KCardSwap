"""
Message ORM model for Social module
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

from app.shared.infrastructure.database.connection import Base


class MessageModel(Base):
    """Message ORM model"""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default="sent",
        server_default="sent",
        index=True,
    )  # sent, delivered, read
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Compound indexes for efficient querying
    __table_args__ = (
        # For polling with after_message_id cursor
        Index("idx_message_room_created", "room_id", "created_at"),
        Index("idx_message_room_id", "room_id", "id"),
        # For unread count queries
        Index("idx_message_status_sender", "room_id", "status", "sender_id"),
    )
