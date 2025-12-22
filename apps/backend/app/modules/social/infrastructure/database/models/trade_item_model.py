"""TradeItem ORM model for Social module"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.shared.infrastructure.database.connection import Base


class TradeItemModel(Base):
    """TradeItem ORM model"""

    __tablename__ = "trade_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_side = Column(
        String(20),
        nullable=False,
    )  # initiator, responder
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    trade = relationship("TradeModel", back_populates="items")

    # Ensure no duplicate cards in same trade
    __table_args__ = (UniqueConstraint("trade_id", "card_id", name="uq_trade_card"),)
