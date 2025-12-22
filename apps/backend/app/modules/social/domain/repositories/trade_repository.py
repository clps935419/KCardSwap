"""Trade Repository Interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.entities.trade_item import TradeItem


class ITradeRepository(ABC):
    """Interface for trade data access."""
    
    @abstractmethod
    async def create(self, trade: Trade, items: List[TradeItem]) -> Trade:
        """
        Create a new trade with items.
        
        Args:
            trade: Trade entity to create
            items: List of trade items
            
        Returns:
            Created trade entity
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, trade_id: UUID) -> Optional[Trade]:
        """
        Get trade by ID.
        
        Args:
            trade_id: Trade ID
            
        Returns:
            Trade entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_items_by_trade_id(self, trade_id: UUID) -> List[TradeItem]:
        """
        Get all items for a trade.
        
        Args:
            trade_id: Trade ID
            
        Returns:
            List of trade items
        """
        pass
    
    @abstractmethod
    async def update(self, trade: Trade) -> Trade:
        """
        Update trade.
        
        Args:
            trade: Trade entity with updated values
            
        Returns:
            Updated trade entity
        """
        pass
    
    @abstractmethod
    async def get_user_trades(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Trade]:
        """
        Get trades for a user (as initiator or responder).
        
        Args:
            user_id: User ID
            limit: Maximum number of trades to return
            offset: Number of trades to skip
            
        Returns:
            List of trades ordered by created_at DESC
        """
        pass
    
    @abstractmethod
    async def get_active_trades_between_users(
        self,
        user_id_1: UUID,
        user_id_2: UUID,
    ) -> List[Trade]:
        """
        Get active trades between two users.
        
        Args:
            user_id_1: First user ID
            user_id_2: Second user ID
            
        Returns:
            List of active trades (draft, proposed, accepted)
        """
        pass
    
    @abstractmethod
    async def count_active_trades_between_users(
        self,
        user_id_1: UUID,
        user_id_2: UUID,
    ) -> int:
        """
        Count active trades between two users.
        
        Args:
            user_id_1: First user ID
            user_id_2: Second user ID
            
        Returns:
            Count of active trades
        """
        pass
