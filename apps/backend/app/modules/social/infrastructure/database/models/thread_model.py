"""
MessageThread ORM model for Social module
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.shared.infrastructure.database.connection import Base


class MessageThreadModel(Base):
    """MessageThread ORM model - unique conversation thread between two users"""

    __tablename__ = "message_threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # user_a_id and user_b_id are stored in normalized order (smaller UUID first)
    # to ensure uniqueness constraint
    user_a_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_b_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        # Ensure only one thread per user pair (normalized order)
        UniqueConstraint("user_a_id", "user_b_id", name="uq_thread_users"),
        Index("idx_thread_user_a", "user_a_id"),
        Index("idx_thread_user_b", "user_b_id"),
        Index("idx_thread_last_message", "last_message_at"),
    )
