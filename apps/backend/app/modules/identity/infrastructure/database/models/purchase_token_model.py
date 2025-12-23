"""
Purchase Token SQLAlchemy Model - For tracking and preventing replay attacks
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.shared.infrastructure.database.connection import Base


class PurchaseTokenModel(Base):
    """
    SQLAlchemy model for subscription_purchase_tokens table.
    Tracks Google Play purchase tokens to prevent replay attacks.
    """
    
    __tablename__ = "subscription_purchase_tokens"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purchase_token = Column(String(1000), nullable=False, unique=True, index=True)  # Google Play token can be long
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(100), nullable=False)
    platform = Column(String(20), nullable=False, default="android")  # "android" or "ios"
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationship
    user = relationship("UserModel", backref="purchase_tokens")
    
    # Indexes
    __table_args__ = (
        Index("ix_purchase_tokens_token", "purchase_token"),
        Index("ix_purchase_tokens_user_id", "user_id"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<PurchaseTokenModel(id={self.id}, user_id={self.user_id}, "
            f"product_id={self.product_id}, platform={self.platform})>"
        )
