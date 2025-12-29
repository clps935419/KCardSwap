"""
Card ORM model for Social module
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.shared.infrastructure.database.connection import Base


class CardModel(Base):
    """Card ORM model"""

    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    idol = Column(String(100), nullable=True)
    idol_group = Column(String(100), nullable=True)
    album = Column(String(100), nullable=True)
    version = Column(String(100), nullable=True)
    rarity = Column(String(50), nullable=True)
    status = Column(
        String(50),
        nullable=False,
        default="available",
        server_default="available",
        index=True,
    )
    image_url = Column(Text, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    upload_status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )
    upload_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationship (will be added when UserModel is extended)
    # owner = relationship("UserModel", back_populates="cards")
