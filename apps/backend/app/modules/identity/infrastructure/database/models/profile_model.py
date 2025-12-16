"""
Profile ORM model for Identity module
"""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.shared.infrastructure.database.connection import Base


class ProfileModel(Base):
    """Profile ORM model"""
    __tablename__ = "profiles"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    nickname = Column(String(100))
    avatar_url = Column(Text)
    bio = Column(Text)
    region = Column(String(100))
    preferences = Column(JSON, default=dict)
    privacy_flags = Column(
        JSON,
        default={
            "nearby_visible": True,
            "show_online": True,
            "allow_stranger_chat": True
        }
    )
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    user = relationship("UserModel", back_populates="profile")
