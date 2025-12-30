"""
Unit tests for GetMyCardsUseCase
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.cards.get_my_cards import (
    GetMyCardsUseCase,
)
from app.modules.social.domain.entities.card import Card


class TestGetMyCardsUseCase:
    """Test GetMyCardsUseCase"""

    @pytest.fixture
    def mock_card_repository(self):
        """Create mock card repository"""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def use_case(self, mock_card_repository):
        """Create use case instance"""
        return GetMyCardsUseCase(card_repository=mock_card_repository)

    @pytest.mark.asyncio
    async def test_get_my_cards_all(self, use_case, mock_card_repository):
        """Test getting all cards without status filter"""
        # Arrange
        owner_id = uuid4()
        card1 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_AVAILABLE)
        card2 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_TRADING)
        card3 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_TRADED)

        mock_card_repository.find_by_owner.return_value = [card1, card2, card3]

        # Act
        result = await use_case.execute(owner_id=owner_id)

        # Assert
        assert len(result) == 3
        assert card1 in result
        assert card2 in result
        assert card3 in result
        mock_card_repository.find_by_owner.assert_called_once_with(owner_id)
        mock_card_repository.find_by_status.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_my_cards_by_status_available(
        self, use_case, mock_card_repository
    ):
        """Test getting cards filtered by available status"""
        # Arrange
        owner_id = uuid4()
        card1 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_AVAILABLE)
        card2 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_AVAILABLE)

        mock_card_repository.find_by_status.return_value = [card1, card2]

        # Act
        result = await use_case.execute(owner_id=owner_id, status=Card.STATUS_AVAILABLE)

        # Assert
        assert len(result) == 2
        assert all(card.status == Card.STATUS_AVAILABLE for card in result)
        mock_card_repository.find_by_status.assert_called_once_with(
            owner_id, Card.STATUS_AVAILABLE
        )
        mock_card_repository.find_by_owner.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_my_cards_by_status_trading(self, use_case, mock_card_repository):
        """Test getting cards filtered by trading status"""
        # Arrange
        owner_id = uuid4()
        card1 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_TRADING)

        mock_card_repository.find_by_status.return_value = [card1]

        # Act
        result = await use_case.execute(owner_id=owner_id, status=Card.STATUS_TRADING)

        # Assert
        assert len(result) == 1
        assert result[0].status == Card.STATUS_TRADING
        mock_card_repository.find_by_status.assert_called_once_with(
            owner_id, Card.STATUS_TRADING
        )

    @pytest.mark.asyncio
    async def test_get_my_cards_by_status_traded(self, use_case, mock_card_repository):
        """Test getting cards filtered by traded status"""
        # Arrange
        owner_id = uuid4()
        card1 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_TRADED)
        card2 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_TRADED)
        card3 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_TRADED)

        mock_card_repository.find_by_status.return_value = [card1, card2, card3]

        # Act
        result = await use_case.execute(owner_id=owner_id, status=Card.STATUS_TRADED)

        # Assert
        assert len(result) == 3
        assert all(card.status == Card.STATUS_TRADED for card in result)
        mock_card_repository.find_by_status.assert_called_once_with(
            owner_id, Card.STATUS_TRADED
        )

    @pytest.mark.asyncio
    async def test_get_my_cards_empty_result(self, use_case, mock_card_repository):
        """Test getting cards when user has no cards"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.find_by_owner.return_value = []

        # Act
        result = await use_case.execute(owner_id=owner_id)

        # Assert
        assert len(result) == 0
        assert result == []
        mock_card_repository.find_by_owner.assert_called_once_with(owner_id)

    @pytest.mark.asyncio
    async def test_get_my_cards_by_status_empty_result(
        self, use_case, mock_card_repository
    ):
        """Test getting cards by status when no cards match"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.find_by_status.return_value = []

        # Act
        result = await use_case.execute(owner_id=owner_id, status=Card.STATUS_TRADING)

        # Assert
        assert len(result) == 0
        assert result == []
        mock_card_repository.find_by_status.assert_called_once_with(
            owner_id, Card.STATUS_TRADING
        )

    @pytest.mark.asyncio
    async def test_get_my_cards_with_metadata(self, use_case, mock_card_repository):
        """Test getting cards returns full card metadata"""
        # Arrange
        owner_id = uuid4()
        card = Card(
            id=uuid4(),
            owner_id=owner_id,
            idol="IU",
            idol_group="Solo",
            album="LILAC",
            version="Standard",
            rarity=Card.RARITY_RARE,
            status=Card.STATUS_AVAILABLE,
            image_url="https://storage.googleapis.com/bucket/cards/user/card.jpg",
            size_bytes=1024 * 500,
        )

        mock_card_repository.find_by_owner.return_value = [card]

        # Act
        result = await use_case.execute(owner_id=owner_id)

        # Assert
        assert len(result) == 1
        retrieved_card = result[0]
        assert retrieved_card.idol == "IU"
        assert retrieved_card.idol_group == "Solo"
        assert retrieved_card.album == "LILAC"
        assert retrieved_card.version == "Standard"
        assert retrieved_card.rarity == Card.RARITY_RARE
        assert retrieved_card.image_url is not None

    @pytest.mark.asyncio
    async def test_get_my_cards_multiple_owners(self, use_case, mock_card_repository):
        """Test that only owner's cards are returned"""
        # Arrange
        owner_id = uuid4()
        other_owner_id = uuid4()

        # Cards for specific owner
        card1 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_AVAILABLE)
        card2 = Card(id=uuid4(), owner_id=owner_id, status=Card.STATUS_TRADING)

        # Card for different owner should not be returned
        other_card = Card(
            id=uuid4(), owner_id=other_owner_id, status=Card.STATUS_AVAILABLE
        )

        mock_card_repository.find_by_owner.return_value = [card1, card2]

        # Act
        result = await use_case.execute(owner_id=owner_id)

        # Assert
        assert len(result) == 2
        assert all(card.owner_id == owner_id for card in result)
        assert other_card not in result

    @pytest.mark.asyncio
    async def test_get_my_cards_preserves_order(self, use_case, mock_card_repository):
        """Test that cards order from repository is preserved"""
        # Arrange
        owner_id = uuid4()
        card1 = Card(id=uuid4(), owner_id=owner_id)
        card2 = Card(id=uuid4(), owner_id=owner_id)
        card3 = Card(id=uuid4(), owner_id=owner_id)

        # Repository returns cards in specific order
        mock_card_repository.find_by_owner.return_value = [card1, card2, card3]

        # Act
        result = await use_case.execute(owner_id=owner_id)

        # Assert
        assert result[0] == card1
        assert result[1] == card2
        assert result[2] == card3
