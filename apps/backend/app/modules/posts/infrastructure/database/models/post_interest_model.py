"""
PostInterest ORM model for Posts module
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

from app.shared.infrastructure.database.connection import Base


class PostInterestModel(Base):
    """PostInterest ORM model"""

    __tablename__ = "post_interests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )  # pending, accepted, rejected
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_user_interest"),
        Index("idx_post_interests_post_id_created_at", "post_id", "created_at"),
        Index("idx_post_interests_user_id_created_at", "user_id", "created_at"),
    )
