"""
Friendship ORM model for Social module
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

from app.shared.infrastructure.database.connection import Base


class FriendshipModel(Base):
    """Friendship ORM model"""

    __tablename__ = "friendships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    friend_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )  # pending, accepted, blocked
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Compound index for efficient friendship lookups
    __table_args__ = (
        Index("idx_friendship_users", "user_id", "friend_id"),
        Index("idx_friendship_status", "status"),
    )
