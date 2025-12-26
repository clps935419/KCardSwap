"""
Rating ORM model for Social module
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID

from app.shared.infrastructure.database.connection import Base


class RatingModel(Base):
    """Rating ORM model"""

    __tablename__ = "ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rater_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rated_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trade_id = Column(
        UUID(as_uuid=True),
        # ForeignKey to trades table will be added when Trade module is implemented
        # nullable=True: Can rate based on friendship alone (FR-SOCIAL-003A)
        nullable=True,
        index=True,
    )
    score = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Compound indexes for efficient querying
    __table_args__ = (
        # For checking duplicate ratings per trade (when trade_id is provided)
        # Note: Partial unique index will be added in migration to handle NULL trade_id
        Index("idx_rating_trade_rater", "trade_id", "rater_id"),
        # For getting user's average rating
        Index("idx_rating_rated_user", "rated_user_id", "score"),
        # For friendship-based ratings (one rating per friend pair, when no trade_id)
        Index("idx_rating_friendship", "rater_id", "rated_user_id"),
    )
