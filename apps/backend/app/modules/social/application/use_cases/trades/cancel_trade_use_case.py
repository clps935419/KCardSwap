"""Cancel Trade Use Case"""

from datetime import datetime
from uuid import UUID

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.repositories.i_card_repository import ICardRepository
from app.modules.social.domain.repositories.i_trade_repository import ITradeRepository
from app.modules.social.domain.services.trade_validation_service import (
    TradeValidationService,
)


class CancelTradeUseCase:
    """
    Use case for canceling a trade.

    Business Rules:
    - Either party can cancel
    - Trade must be in 'draft', 'proposed', or 'accepted' status
    - Transitions status to 'canceled'
    - Returns cards to 'available' status
    - Sets canceled_at timestamp
    """

    def __init__(
        self,
        trade_repository: ITradeRepository,
        card_repository: ICardRepository,
        validation_service: TradeValidationService,
    ):
        self.trade_repository = trade_repository
        self.card_repository = card_repository
        self.validation_service = validation_service

    async def execute(self, trade_id: UUID, user_id: UUID) -> Trade:
        """
        Cancel a trade.

        Args:
            trade_id: ID of trade to cancel
            user_id: ID of user canceling (must be participant)

        Returns:
            Updated Trade entity

        Raises:
            ValueError: If trade not found or cannot be canceled
        """
        # Get trade
        trade = await self.trade_repository.get_by_id(trade_id)
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")

        # Validate user can cancel
        self.validation_service.validate_user_can_cancel(trade, user_id)

        # Get trade items and release cards
        items = await self.trade_repository.get_items_by_trade_id(trade_id)
        for item in items:
            card = await self.card_repository.find_by_id(item.card_id)
            if card and card.status == "trading":
                card.set_status("available")
                await self.card_repository.save(card)

        # Update trade
        trade.status = Trade.STATUS_CANCELED
        trade.canceled_at = datetime.utcnow()
        trade.updated_at = datetime.utcnow()

        # Save and return
        return await self.trade_repository.update(trade)
