"""
Unit tests for TradeRepositoryImpl

Tests the trade repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.entities.trade_item import TradeItem
from app.modules.social.infrastructure.database.models.trade_model import TradeModel
from app.modules.social.infrastructure.repositories.trade_repository_impl import (
    TradeRepositoryImpl,
)


class TestTradeRepositoryImpl:
    """Test TradeRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return TradeRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_trade(self):
        """Create sample Trade entity"""
        return Trade(
            id=uuid4(),
            initiator_id=uuid4(),
            responder_id=uuid4(),
            status="proposed",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_trade_items(self, sample_trade):
        """Create sample TradeItem entities"""
        return [
            TradeItem(
                id=uuid4(),
                trade_id=sample_trade.id,
                card_id=uuid4(),
                owner_side="initiator",
                created_at=datetime.utcnow(),
            ),
            TradeItem(
                id=uuid4(),
                trade_id=sample_trade.id,
                card_id=uuid4(),
                owner_side="responder",
                created_at=datetime.utcnow(),
            ),
        ]

    @pytest.fixture
    def sample_trade_model(self, sample_trade):
        """Create sample TradeModel"""
        return TradeModel(
            id=sample_trade.id,
            initiator_id=sample_trade.initiator_id,
            responder_id=sample_trade.responder_id,
            status=sample_trade.status,  # status is already a string
            created_at=sample_trade.created_at,
            updated_at=sample_trade.updated_at,
        )

    @pytest.mark.asyncio
    async def test_create_trade(
        self, repository, mock_session, sample_trade, sample_trade_items
    ):
        """Test creating a trade with items"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_trade, sample_trade_items)

        # Assert
        assert result is not None
        assert result.id == sample_trade.id
        # add should be called for trade + items
        assert mock_session.add.call_count >= 1

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_trade_model):
        """Test getting trade by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_trade_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(sample_trade_model.id)

        # Assert
        assert result is not None
        assert result.id == sample_trade_model.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting trade by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(uuid4())

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_items_by_trade_id(self, repository, mock_session):
        """Test getting trade items by trade ID"""
        # Arrange
        trade_id = uuid4()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_items_by_trade_id(trade_id)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_trade(
        self, repository, mock_session, sample_trade, sample_trade_model
    ):
        """Test updating a trade"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_trade_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Modify the trade
        sample_trade.status = "accepted"

        # Act
        result = await repository.update(sample_trade)

        # Assert
        assert result is not None
        assert result.id == sample_trade.id

    @pytest.mark.asyncio
    async def test_get_user_trades(self, repository, mock_session):
        """Test getting trades for a user"""
        # Arrange
        user_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_user_trades(user_id, limit=10, offset=0)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_trades_between_users(self, repository, mock_session):
        """Test getting active trades between two users"""
        # Arrange
        user_id_1 = uuid4()
        user_id_2 = uuid4()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_active_trades_between_users(user_id_1, user_id_2)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_active_trades_between_users(self, repository, mock_session):
        """Test counting active trades between two users"""
        # Arrange
        user_id_1 = uuid4()
        user_id_2 = uuid4()
        expected_count = 3

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.count_active_trades_between_users(
            user_id_1, user_id_2
        )

        # Assert
        assert result == expected_count
