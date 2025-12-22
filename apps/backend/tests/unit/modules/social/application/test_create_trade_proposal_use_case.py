"""
Unit tests for CreateTradeProposalUseCase (T164)
Testing trade proposal creation business rules with mocked dependencies
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.modules.social.application.use_cases.trades.create_trade_proposal_use_case import (
    CreateTradeProposalUseCase,
    CreateTradeProposalRequest,
)
from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus


class TestCreateTradeProposalUseCaseSuccess:
    """Test successful trade proposal creation scenarios"""

    @pytest.fixture
    def mock_repositories(self):
        """Setup mock repositories"""
        trade_repo = Mock()
        trade_repo.count_active_trades_between_users = AsyncMock(return_value=0)
        trade_repo.create = AsyncMock(side_effect=lambda trade, items: trade)

        card_repo = Mock()
        friendship_repo = Mock()

        friendship = Friendship(
            id=str(uuid4()),
            user_id=str(uuid4()),
            friend_id=str(uuid4()),
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )
        friendship_repo.get_by_users = AsyncMock(return_value=friendship)

        validation_service = Mock()
        validation_service.validate_card_ownership = Mock()
        validation_service.validate_card_availability = Mock()
        validation_service.validate_trade_items = Mock()

        return {
            "trade_repo": trade_repo,
            "card_repo": card_repo,
            "friendship_repo": friendship_repo,
            "validation_service": validation_service,
        }

    @pytest.mark.asyncio
    async def test_create_trade_proposal_with_valid_data(self, mock_repositories):
        """Test creating trade proposal with valid data"""
        initiator_id = uuid4()
        responder_id = uuid4()
        initiator_card_id = uuid4()
        responder_card_id = uuid4()

        # Setup mock cards
        initiator_card = Card(
            owner_id=initiator_id,
            id=initiator_card_id,
            status=Card.STATUS_AVAILABLE,
        )
        responder_card = Card(
            owner_id=responder_id,
            id=responder_card_id,
            status=Card.STATUS_AVAILABLE,
        )

        mock_repositories["card_repo"].find_by_id = AsyncMock(
            side_effect=[initiator_card, responder_card]
        )
        mock_repositories["card_repo"].save = AsyncMock(side_effect=lambda card: card)

        use_case = CreateTradeProposalUseCase(
            trade_repository=mock_repositories["trade_repo"],
            card_repository=mock_repositories["card_repo"],
            friendship_repository=mock_repositories["friendship_repo"],
            validation_service=mock_repositories["validation_service"],
        )

        request = CreateTradeProposalRequest(
            initiator_id=initiator_id,
            responder_id=responder_id,
            initiator_card_ids=[initiator_card_id],
            responder_card_ids=[responder_card_id],
        )

        trade = await use_case.execute(request)

        assert isinstance(trade, Trade)
        assert trade.initiator_id == initiator_id
        assert trade.responder_id == responder_id
        assert trade.status == Trade.STATUS_PROPOSED

        # Verify friendship check
        mock_repositories["friendship_repo"].get_by_users.assert_called_once()

        # Verify cards were marked as trading
        assert mock_repositories["card_repo"].save.call_count == 2


class TestCreateTradeProposalUseCaseValidation:
    """Test trade proposal validation failures"""

    @pytest.fixture
    def mock_repositories(self):
        """Setup minimal mocks"""
        trade_repo = Mock()
        card_repo = Mock()
        friendship_repo = Mock()
        validation_service = Mock()

        return {
            "trade_repo": trade_repo,
            "card_repo": card_repo,
            "friendship_repo": friendship_repo,
            "validation_service": validation_service,
        }

    @pytest.mark.asyncio
    async def test_cannot_create_trade_with_self(self, mock_repositories):
        """Test cannot create trade with yourself"""
        use_case = CreateTradeProposalUseCase(
            trade_repository=mock_repositories["trade_repo"],
            card_repository=mock_repositories["card_repo"],
            friendship_repository=mock_repositories["friendship_repo"],
            validation_service=mock_repositories["validation_service"],
        )

        user_id = uuid4()
        request = CreateTradeProposalRequest(
            initiator_id=user_id,
            responder_id=user_id,  # Same user
            initiator_card_ids=[uuid4()],
            responder_card_ids=[uuid4()],
        )

        with pytest.raises(ValueError, match="Cannot create trade with yourself"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_cannot_create_trade_without_initiator_cards(self, mock_repositories):
        """Test initiator must provide at least one card"""
        use_case = CreateTradeProposalUseCase(
            trade_repository=mock_repositories["trade_repo"],
            card_repository=mock_repositories["card_repo"],
            friendship_repository=mock_repositories["friendship_repo"],
            validation_service=mock_repositories["validation_service"],
        )

        request = CreateTradeProposalRequest(
            initiator_id=uuid4(),
            responder_id=uuid4(),
            initiator_card_ids=[],  # Empty
            responder_card_ids=[uuid4()],
        )

        with pytest.raises(ValueError, match="Initiator must provide at least one card"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_cannot_create_trade_without_responder_cards(self, mock_repositories):
        """Test responder must provide at least one card"""
        use_case = CreateTradeProposalUseCase(
            trade_repository=mock_repositories["trade_repo"],
            card_repository=mock_repositories["card_repo"],
            friendship_repository=mock_repositories["friendship_repo"],
            validation_service=mock_repositories["validation_service"],
        )

        request = CreateTradeProposalRequest(
            initiator_id=uuid4(),
            responder_id=uuid4(),
            initiator_card_ids=[uuid4()],
            responder_card_ids=[],  # Empty
        )

        with pytest.raises(ValueError, match="Responder must provide at least one card"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_cannot_create_trade_with_non_friends(self, mock_repositories):
        """Test can only create trades with friends"""
        mock_repositories["friendship_repo"].get_by_users = AsyncMock(return_value=None)

        use_case = CreateTradeProposalUseCase(
            trade_repository=mock_repositories["trade_repo"],
            card_repository=mock_repositories["card_repo"],
            friendship_repository=mock_repositories["friendship_repo"],
            validation_service=mock_repositories["validation_service"],
        )

        request = CreateTradeProposalRequest(
            initiator_id=uuid4(),
            responder_id=uuid4(),
            initiator_card_ids=[uuid4()],
            responder_card_ids=[uuid4()],
        )

        with pytest.raises(ValueError, match="Can only create trades with friends"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_cannot_exceed_max_active_trades(self, mock_repositories):
        """Test max active trades limit is enforced"""
        # Setup: already have 3 active trades
        mock_repositories["trade_repo"].count_active_trades_between_users = AsyncMock(
            return_value=3
        )

        friendship = Friendship(
            id=str(uuid4()),
            user_id=str(uuid4()),
            friend_id=str(uuid4()),
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )
        mock_repositories["friendship_repo"].get_by_users = AsyncMock(
            return_value=friendship
        )

        use_case = CreateTradeProposalUseCase(
            trade_repository=mock_repositories["trade_repo"],
            card_repository=mock_repositories["card_repo"],
            friendship_repository=mock_repositories["friendship_repo"],
            validation_service=mock_repositories["validation_service"],
            max_active_trades_per_pair=3,
        )

        request = CreateTradeProposalRequest(
            initiator_id=uuid4(),
            responder_id=uuid4(),
            initiator_card_ids=[uuid4()],
            responder_card_ids=[uuid4()],
        )

        with pytest.raises(ValueError, match="Maximum.*active trades.*exceeded"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_cannot_create_trade_with_nonexistent_card(self, mock_repositories):
        """Test card must exist"""
        mock_repositories["card_repo"].find_by_id = AsyncMock(return_value=None)

        friendship = Friendship(
            id=str(uuid4()),
            user_id=str(uuid4()),
            friend_id=str(uuid4()),
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )
        mock_repositories["friendship_repo"].get_by_users = AsyncMock(
            return_value=friendship
        )
        mock_repositories["trade_repo"].count_active_trades_between_users = AsyncMock(
            return_value=0
        )

        use_case = CreateTradeProposalUseCase(
            trade_repository=mock_repositories["trade_repo"],
            card_repository=mock_repositories["card_repo"],
            friendship_repository=mock_repositories["friendship_repo"],
            validation_service=mock_repositories["validation_service"],
        )

        request = CreateTradeProposalRequest(
            initiator_id=uuid4(),
            responder_id=uuid4(),
            initiator_card_ids=[uuid4()],
            responder_card_ids=[uuid4()],
        )

        with pytest.raises(ValueError, match="Card.*not found"):
            await use_case.execute(request)
