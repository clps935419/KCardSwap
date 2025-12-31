"""
Post ORM model for Posts module
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.shared.infrastructure.database.connection import Base


class PostModel(Base):
    """Post ORM model"""

    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    city_code = Column(String(20), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    content = Column(Text, nullable=False)
    idol = Column(String(100), nullable=True, index=True)
    idol_group = Column(String(100), nullable=True, index=True)
    status = Column(
        String(20),
        nullable=False,
        default="open",
        server_default="open",
        index=True,
    )  # open, closed, expired, deleted
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Compound indexes for efficient queries
    __table_args__ = (
        Index("idx_posts_board_status_created_at", "city_code", "status", "created_at"),
        Index("idx_posts_owner_id", "owner_id"),
    )
