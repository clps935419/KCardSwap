"""SQLAlchemy Trade Repository Implementation"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.entities.trade_item import TradeItem
from app.modules.social.domain.repositories.trade_repository import ITradeRepository
from app.modules.social.infrastructure.database.models.trade_model import TradeModel
from app.modules.social.infrastructure.database.models.trade_item_model import (
    TradeItemModel,
)


class SQLAlchemyTradeRepository(ITradeRepository):
    """SQLAlchemy implementation of Trade repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, trade: Trade, items: List[TradeItem]) -> Trade:
        """Create a new trade with items"""
        # Create trade model
        trade_model = TradeModel(
            id=trade.id,
            initiator_id=trade.initiator_id,
            responder_id=trade.responder_id,
            status=trade.status,
            accepted_at=trade.accepted_at,
            initiator_confirmed_at=trade.initiator_confirmed_at,
            responder_confirmed_at=trade.responder_confirmed_at,
            completed_at=trade.completed_at,
            canceled_at=trade.canceled_at,
            created_at=trade.created_at,
            updated_at=trade.updated_at,
        )
        self.session.add(trade_model)
        
        # Create item models
        for item in items:
            item_model = TradeItemModel(
                id=item.id,
                trade_id=item.trade_id,
                card_id=item.card_id,
                owner_side=item.owner_side,
                created_at=item.created_at,
            )
            self.session.add(item_model)
        
        await self.session.flush()
        await self.session.refresh(trade_model)
        
        return self._to_entity(trade_model)

    async def get_by_id(self, trade_id: UUID) -> Optional[Trade]:
        """Get trade by ID"""
        result = await self.session.execute(
            select(TradeModel)
            .options(selectinload(TradeModel.items))
            .where(TradeModel.id == trade_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_items_by_trade_id(self, trade_id: UUID) -> List[TradeItem]:
        """Get all items for a trade"""
        result = await self.session.execute(
            select(TradeItemModel).where(TradeItemModel.trade_id == trade_id)
        )
        models = result.scalars().all()
        return [self._item_to_entity(model) for model in models]

    async def update(self, trade: Trade) -> Trade:
        """Update trade"""
        result = await self.session.execute(
            select(TradeModel).where(TradeModel.id == trade.id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Trade {trade.id} not found")
        
        # Update fields
        model.status = trade.status
        model.accepted_at = trade.accepted_at
        model.initiator_confirmed_at = trade.initiator_confirmed_at
        model.responder_confirmed_at = trade.responder_confirmed_at
        model.completed_at = trade.completed_at
        model.canceled_at = trade.canceled_at
        model.updated_at = trade.updated_at
        
        await self.session.flush()
        await self.session.refresh(model)
        
        return self._to_entity(model)

    async def get_user_trades(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Trade]:
        """Get trades for a user (as initiator or responder)"""
        result = await self.session.execute(
            select(TradeModel)
            .options(selectinload(TradeModel.items))
            .where(
                or_(
                    TradeModel.initiator_id == user_id,
                    TradeModel.responder_id == user_id,
                )
            )
            .order_by(TradeModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_active_trades_between_users(
        self,
        user_id_1: UUID,
        user_id_2: UUID,
    ) -> List[Trade]:
        """Get active trades between two users"""
        active_statuses = [
            Trade.STATUS_DRAFT,
            Trade.STATUS_PROPOSED,
            Trade.STATUS_ACCEPTED,
        ]
        
        result = await self.session.execute(
            select(TradeModel)
            .options(selectinload(TradeModel.items))
            .where(
                and_(
                    or_(
                        and_(
                            TradeModel.initiator_id == user_id_1,
                            TradeModel.responder_id == user_id_2,
                        ),
                        and_(
                            TradeModel.initiator_id == user_id_2,
                            TradeModel.responder_id == user_id_1,
                        ),
                    ),
                    TradeModel.status.in_(active_statuses),
                )
            )
            .order_by(TradeModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count_active_trades_between_users(
        self,
        user_id_1: UUID,
        user_id_2: UUID,
    ) -> int:
        """Count active trades between two users"""
        active_statuses = [
            Trade.STATUS_DRAFT,
            Trade.STATUS_PROPOSED,
            Trade.STATUS_ACCEPTED,
        ]
        
        result = await self.session.execute(
            select(func.count(TradeModel.id)).where(
                and_(
                    or_(
                        and_(
                            TradeModel.initiator_id == user_id_1,
                            TradeModel.responder_id == user_id_2,
                        ),
                        and_(
                            TradeModel.initiator_id == user_id_2,
                            TradeModel.responder_id == user_id_1,
                        ),
                    ),
                    TradeModel.status.in_(active_statuses),
                )
            )
        )
        count = result.scalar_one()
        return count

    def _to_entity(self, model: TradeModel) -> Trade:
        """Convert ORM model to domain entity"""
        return Trade(
            id=model.id,
            initiator_id=model.initiator_id,
            responder_id=model.responder_id,
            status=model.status,
            accepted_at=model.accepted_at,
            initiator_confirmed_at=model.initiator_confirmed_at,
            responder_confirmed_at=model.responder_confirmed_at,
            completed_at=model.completed_at,
            canceled_at=model.canceled_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _item_to_entity(self, model: TradeItemModel) -> TradeItem:
        """Convert TradeItem ORM model to domain entity"""
        return TradeItem(
            id=model.id,
            trade_id=model.trade_id,
            card_id=model.card_id,
            owner_side=model.owner_side,
            created_at=model.created_at,
        )
