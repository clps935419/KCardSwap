"""Trade ORM model for Social module"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.shared.infrastructure.database.connection import Base


class TradeModel(Base):
    """Trade ORM model"""

    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    responder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        String(20),
        nullable=False,
        default="proposed",
        server_default="proposed",
        index=True,
    )  # draft, proposed, accepted, completed, rejected, canceled
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    initiator_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    responder_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    items = relationship(
        "TradeItemModel",
        back_populates="trade",
        cascade="all, delete-orphan",
    )

    # Compound indexes for efficient lookups
    __table_args__ = (
        Index("idx_trades_initiator_created", "initiator_id", "created_at"),
        Index("idx_trades_responder_created", "responder_id", "created_at"),
        Index("idx_trades_status_created", "status", "created_at"),
    )
