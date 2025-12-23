"""
Subscription SQLAlchemy Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.shared.infrastructure.database.base import Base


class SubscriptionModel(Base):
    """SQLAlchemy model for subscriptions table"""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan = Column(String(20), nullable=False, default="free")  # "free" or "premium"
    status = Column(String(20), nullable=False, default="inactive")  # "active", "inactive", "expired", "pending"
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("UserModel", back_populates="subscription")
    
    # Indexes
    __table_args__ = (
        Index("ix_subscriptions_user_id", "user_id"),
        Index("ix_subscriptions_status_expires_at", "status", "expires_at"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<SubscriptionModel(id={self.id}, user_id={self.user_id}, "
            f"plan={self.plan}, status={self.status})>"
        )
