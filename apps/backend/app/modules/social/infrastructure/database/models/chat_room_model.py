"""
ChatRoom ORM model for Social module
"""
import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID

from app.shared.infrastructure.database.connection import Base


class ChatRoomModel(Base):
    """ChatRoom ORM model"""

    __tablename__ = "chat_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Store participant IDs as array (always 2 participants, sorted)
    participant_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Index on participant_ids for efficient lookups
    __table_args__ = (Index("idx_chat_room_participants", "participant_ids"),)
