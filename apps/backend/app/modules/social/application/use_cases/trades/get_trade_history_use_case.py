"""Get Trade History Use Case"""

from typing import List
from uuid import UUID

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.repositories.i_trade_repository import ITradeRepository


class GetTradeHistoryUseCase:
    """
    Use case for retrieving user's trade history.

    Returns all trades where user is initiator or responder,
    ordered by created_at DESC (newest first).
    """

    def __init__(self, trade_repository: ITradeRepository):
        self.trade_repository = trade_repository

    async def execute(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Trade]:
        """
        Get trade history for a user.

        Args:
            user_id: User ID to get trades for
            limit: Maximum number of trades to return (default: 50)
            offset: Number of trades to skip (default: 0)

        Returns:
            List of trades ordered by created_at DESC
        """
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")

        if offset < 0:
            raise ValueError("Offset must be >= 0")

        trades = await self.trade_repository.get_user_trades(
            user_id,
            limit=limit,
            offset=offset,
        )

        return trades
