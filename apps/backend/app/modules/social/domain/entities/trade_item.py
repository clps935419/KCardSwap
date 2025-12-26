"""TradeItem Entity - represents a card in a trade."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class TradeItem:
    """
    TradeItem entity representing a card in a trade.

    Attributes:
        id: Unique identifier
        trade_id: Trade this item belongs to
        card_id: Card being traded
        owner_side: Which party owns this card (initiator/responder)
        created_at: Timestamp when item was created
    """

    id: UUID
    trade_id: UUID
    card_id: UUID
    owner_side: str
    created_at: Optional[datetime] = None

    # Valid owner_side values
    SIDE_INITIATOR = "initiator"
    SIDE_RESPONDER = "responder"

    VALID_SIDES = {SIDE_INITIATOR, SIDE_RESPONDER}

    def __post_init__(self):
        """Validate entity invariants."""
        if self.owner_side not in self.VALID_SIDES:
            raise ValueError(f"Invalid owner_side: {self.owner_side}")

    def is_from_initiator(self) -> bool:
        """Check if this card is from initiator."""
        return self.owner_side == self.SIDE_INITIATOR

    def is_from_responder(self) -> bool:
        """Check if this card is from responder."""
        return self.owner_side == self.SIDE_RESPONDER
