"""Accept Trade Use Case"""

from datetime import datetime
from uuid import UUID

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.repositories.trade_repository import ITradeRepository
from app.modules.social.domain.services.trade_validation_service import (
    TradeValidationService,
)


class AcceptTradeUseCase:
    """
    Use case for accepting a trade proposal.

    Business Rules:
    - Only responder can accept
    - Trade must be in 'proposed' status
    - Sets accepted_at timestamp
    - Transitions status to 'accepted'
    """

    def __init__(
        self,
        trade_repository: ITradeRepository,
        validation_service: TradeValidationService,
    ):
        self.trade_repository = trade_repository
        self.validation_service = validation_service

    async def execute(self, trade_id: UUID, user_id: UUID) -> Trade:
        """
        Accept a trade proposal.

        Args:
            trade_id: ID of trade to accept
            user_id: ID of user accepting (must be responder)

        Returns:
            Updated Trade entity

        Raises:
            ValueError: If trade not found or cannot be accepted
        """
        # Get trade
        trade = await self.trade_repository.get_by_id(trade_id)
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")

        # Validate user can accept
        self.validation_service.validate_user_can_accept(trade, user_id)

        # Update trade
        trade.status = Trade.STATUS_ACCEPTED
        trade.accepted_at = datetime.utcnow()
        trade.updated_at = datetime.utcnow()

        # Save and return
        return await self.trade_repository.update(trade)
