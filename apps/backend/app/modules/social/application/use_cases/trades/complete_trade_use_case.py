"""Complete Trade Use Case"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.repositories.card_repository import CardRepository
from app.modules.social.domain.repositories.trade_repository import ITradeRepository
from app.modules.social.domain.services.trade_validation_service import (
    TradeValidationService,
)


class CompleteTradeUseCase:
    """
    Use case for confirming trade completion.
    
    Business Rules:
    - Only participants can confirm
    - Trade must be in 'accepted' status
    - Each party confirms independently
    - When both confirm, status becomes 'completed'
    - Cards are marked as 'traded'
    - Sets *_confirmed_at timestamp for confirming party
    - Sets completed_at when both have confirmed
    - Enforces 48h timeout: if accepted_at + timeout < now, auto-cancel
    """
    
    def __init__(
        self,
        trade_repository: ITradeRepository,
        card_repository: CardRepository,
        validation_service: TradeValidationService,
        confirmation_timeout_hours: int = 48,
    ):
        self.trade_repository = trade_repository
        self.card_repository = card_repository
        self.validation_service = validation_service
        self.confirmation_timeout_hours = confirmation_timeout_hours
    
    async def execute(self, trade_id: UUID, user_id: UUID) -> Trade:
        """
        Confirm trade completion for one party.
        
        Args:
            trade_id: ID of trade to complete
            user_id: ID of user confirming (must be participant)
            
        Returns:
            Updated Trade entity
            
        Raises:
            ValueError: If trade not found, cannot be completed, or has timed out
        """
        # Get trade
        trade = await self.trade_repository.get_by_id(trade_id)
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        # Check for timeout (48h rule)
        if trade.status == Trade.STATUS_ACCEPTED and trade.accepted_at:
            timeout = timedelta(hours=self.confirmation_timeout_hours)
            if datetime.utcnow() > trade.accepted_at + timeout:
                # Auto-cancel due to timeout
                trade.status = Trade.STATUS_CANCELED
                trade.canceled_at = datetime.utcnow()
                trade.updated_at = datetime.utcnow()
                
                # Release cards
                items = await self.trade_repository.get_items_by_trade_id(trade_id)
                for item in items:
                    card = await self.card_repository.find_by_id(item.card_id)
                    if card and card.status == "trading":
                        card.set_status("available")
                        await self.card_repository.save(card)
                
                await self.trade_repository.update(trade)
                raise ValueError(
                    f"Trade has been automatically canceled due to "
                    f"{self.confirmation_timeout_hours}h timeout"
                )
        
        # Validate user can confirm
        self.validation_service.validate_user_can_confirm(trade, user_id)
        
        now = datetime.utcnow()
        
        # Mark confirmation for this user
        if trade.is_initiator(user_id):
            if trade.initiator_confirmed_at:
                raise ValueError("Initiator has already confirmed")
            trade.initiator_confirmed_at = now
        elif trade.is_responder(user_id):
            if trade.responder_confirmed_at:
                raise ValueError("Responder has already confirmed")
            trade.responder_confirmed_at = now
        
        trade.updated_at = now
        
        # Check if both have confirmed
        if trade.is_completed():
            # Mark trade as completed
            trade.status = Trade.STATUS_COMPLETED
            trade.completed_at = now
            
            # Mark all cards as traded
            items = await self.trade_repository.get_items_by_trade_id(trade_id)
            for item in items:
                card = await self.card_repository.find_by_id(item.card_id)
                if card:
                    card.set_status("traded")
                    await self.card_repository.save(card)
        
        # Save and return
        return await self.trade_repository.update(trade)
