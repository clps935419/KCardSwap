"""
MessageRequest ORM model for Social module
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.shared.infrastructure.database.connection import Base


class MessageRequestModel(Base):
    """MessageRequest ORM model - stores pending message requests from strangers"""

    __tablename__ = "message_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    initial_message = Column(Text, nullable=False)
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True,
    )
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )  # pending, accepted, declined
    thread_id = Column(
        UUID(as_uuid=True),
        ForeignKey("message_threads.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index("idx_message_request_recipient_status", "recipient_id", "status"),
        Index("idx_message_request_users", "sender_id", "recipient_id"),
    )
