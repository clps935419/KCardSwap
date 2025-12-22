"""Reject Trade Use Case"""

from datetime import datetime
from uuid import UUID

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.repositories.card_repository import CardRepository
from app.modules.social.domain.repositories.trade_repository import ITradeRepository
from app.modules.social.domain.services.trade_validation_service import (
    TradeValidationService,
)


class RejectTradeUseCase:
    """
    Use case for rejecting a trade proposal.
    
    Business Rules:
    - Only responder can reject
    - Trade must be in 'proposed' or 'draft' status
    - Transitions status to 'rejected'
    - Returns cards to 'available' status
    """
    
    def __init__(
        self,
        trade_repository: ITradeRepository,
        card_repository: CardRepository,
        validation_service: TradeValidationService,
    ):
        self.trade_repository = trade_repository
        self.card_repository = card_repository
        self.validation_service = validation_service
    
    async def execute(self, trade_id: UUID, user_id: UUID) -> Trade:
        """
        Reject a trade proposal.
        
        Args:
            trade_id: ID of trade to reject
            user_id: ID of user rejecting (must be responder)
            
        Returns:
            Updated Trade entity
            
        Raises:
            ValueError: If trade not found or cannot be rejected
        """
        # Get trade
        trade = await self.trade_repository.get_by_id(trade_id)
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        # Validate user can reject
        self.validation_service.validate_user_can_reject(trade, user_id)
        
        # Get trade items and release cards
        items = await self.trade_repository.get_items_by_trade_id(trade_id)
        for item in items:
            card = await self.card_repository.find_by_id(item.card_id)
            if card and card.status == "trading":
                card.set_status("available")
                await self.card_repository.save(card)
        
        # Update trade
        trade.status = Trade.STATUS_REJECTED
        trade.updated_at = datetime.utcnow()
        
        # Save and return
        return await self.trade_repository.update(trade)
