"""
Post ORM model for Posts module
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

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
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Compound indexes for efficient queries
    __table_args__ = (
        Index("idx_posts_board_status_created_at", "city_code", "status", "created_at"),
        Index("idx_posts_owner_id", "owner_id"),
    )
