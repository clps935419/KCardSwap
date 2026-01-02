"""Create Trade Proposal Use Case"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.entities.trade_item import TradeItem
from app.modules.social.domain.repositories.i_card_repository import ICardRepository
from app.modules.social.domain.repositories.i_friendship_repository import (
    IFriendshipRepository,
)
from app.modules.social.domain.repositories.i_trade_repository import ITradeRepository
from app.modules.social.domain.services.trade_validation_service import (
    TradeValidationService,
)


class CreateTradeProposalRequest:
    """Request DTO for creating a trade proposal"""

    def __init__(
        self,
        initiator_id: UUID,
        responder_id: UUID,
        initiator_card_ids: List[UUID],
        responder_card_ids: List[UUID],
    ):
        self.initiator_id = initiator_id
        self.responder_id = responder_id
        self.initiator_card_ids = initiator_card_ids
        self.responder_card_ids = responder_card_ids


class CreateTradeProposalUseCase:
    """
    Use case for creating a trade proposal.

    Business Rules:
    - Initiator and responder must be different users
    - Both parties must provide at least one card
    - All cards must exist and be owned by the correct party
    - All cards must be available (not already trading/traded)
    - Users must be friends
    - Maximum active trades between two users is limited (configurable)
    """

    def __init__(
        self,
        trade_repository: ITradeRepository,
        card_repository: ICardRepository,
        friendship_repository: IFriendshipRepository,
        validation_service: TradeValidationService,
        max_active_trades_per_pair: int = 3,
    ):
        self.trade_repository = trade_repository
        self.card_repository = card_repository
        self.friendship_repository = friendship_repository
        self.validation_service = validation_service
        self.max_active_trades_per_pair = max_active_trades_per_pair

    async def execute(self, request: CreateTradeProposalRequest) -> Trade:
        """
        Create a trade proposal.

        Args:
            request: CreateTradeProposalRequest containing trade details

        Returns:
            Created Trade entity

        Raises:
            ValueError: If trade proposal is invalid
        """
        # Validate: different users
        if request.initiator_id == request.responder_id:
            raise ValueError("Cannot create trade with yourself")

        # Validate: at least one card from each side
        if not request.initiator_card_ids:
            raise ValueError("Initiator must provide at least one card")
        if not request.responder_card_ids:
            raise ValueError("Responder must provide at least one card")

        # Validate: users are friends
        friendship = await self.friendship_repository.get_by_users(
            str(request.initiator_id),
            str(request.responder_id),
        )
        if not friendship or not friendship.is_accepted():
            raise ValueError("Can only create trades with friends")

        # Validate: not too many active trades
        active_count = await self.trade_repository.count_active_trades_between_users(
            request.initiator_id,
            request.responder_id,
        )
        if active_count >= self.max_active_trades_per_pair:
            raise ValueError(
                f"Maximum of {self.max_active_trades_per_pair} active trades "
                f"between users exceeded"
            )

        # Fetch and validate initiator cards
        initiator_cards = []
        for card_id in request.initiator_card_ids:
            card = await self.card_repository.find_by_id(card_id)
            if not card:
                raise ValueError(f"Card {card_id} not found")
            initiator_cards.append(card)

        self.validation_service.validate_card_ownership(
            initiator_cards,
            request.initiator_id,
            "initiator",
        )
        self.validation_service.validate_card_availability(initiator_cards)

        # Fetch and validate responder cards
        responder_cards = []
        for card_id in request.responder_card_ids:
            card = await self.card_repository.find_by_id(card_id)
            if not card:
                raise ValueError(f"Card {card_id} not found")
            responder_cards.append(card)

        self.validation_service.validate_card_ownership(
            responder_cards,
            request.responder_id,
            "responder",
        )
        self.validation_service.validate_card_availability(responder_cards)

        # Create trade entity
        trade_id = uuid4()
        now = datetime.now(timezone.utc)

        trade = Trade(
            id=trade_id,
            initiator_id=request.initiator_id,
            responder_id=request.responder_id,
            status=Trade.STATUS_PROPOSED,
            created_at=now,
            updated_at=now,
        )

        # Create trade items
        items = []

        for card_id in request.initiator_card_ids:
            items.append(
                TradeItem(
                    id=uuid4(),
                    trade_id=trade_id,
                    card_id=card_id,
                    owner_side=TradeItem.SIDE_INITIATOR,
                    created_at=now,
                )
            )

        for card_id in request.responder_card_ids:
            items.append(
                TradeItem(
                    id=uuid4(),
                    trade_id=trade_id,
                    card_id=card_id,
                    owner_side=TradeItem.SIDE_RESPONDER,
                    created_at=now,
                )
            )

        # Validate trade items
        self.validation_service.validate_trade_items(
            items,
            request.initiator_id,
            request.responder_id,
        )

        # Mark cards as trading
        for card in initiator_cards + responder_cards:
            card.mark_as_trading()
            await self.card_repository.save(card)

        # Save trade with items
        created_trade = await self.trade_repository.create(trade, items)

        return created_trade
