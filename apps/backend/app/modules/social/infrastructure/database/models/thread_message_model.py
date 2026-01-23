"""
ThreadMessage ORM model for Social module
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID

from app.shared.infrastructure.database.connection import Base


class ThreadMessageModel(Base):
    """ThreadMessage ORM model - messages in a conversation thread"""

    __tablename__ = "thread_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(
        UUID(as_uuid=True),
        ForeignKey("message_threads.id", ondelete="CASCADE"),
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
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_thread_message_thread_created", "thread_id", "created_at"),
    )
