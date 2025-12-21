"""
Unit tests for SearchNearbyCardsUseCase
"""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.config import settings
from app.modules.social.application.dtos.nearby_dtos import (
    SearchNearbyRequest,
    NearbyCardResult,
)
from app.modules.social.application.use_cases.nearby import (
    SearchNearbyCardsUseCase,
    RateLimitExceededException,
)
from app.modules.social.domain.entities.card import Card


@pytest.fixture
def mock_card_repository():
    """Mock card repository"""
    return AsyncMock()


@pytest.fixture
def mock_quota_service():
    """Mock search quota service"""
    return AsyncMock()


@pytest.fixture
def use_case(mock_card_repository, mock_quota_service):
    """Create use case instance with mocks"""
    return SearchNearbyCardsUseCase(
        card_repository=mock_card_repository,
        quota_service=mock_quota_service,
    )


class TestSearchNearbyCardsUseCase:
    """Test suite for SearchNearbyCardsUseCase"""

    @pytest.mark.asyncio
    async def test_search_success_free_user(
        self, use_case, mock_card_repository, mock_quota_service
    ):
        """Test successful search for free user"""
        # Arrange
        user_id = uuid4()
        owner_id = uuid4()
        card_id = uuid4()

        request = SearchNearbyRequest(
            user_id=user_id, lat=25.0330, lng=121.5654, radius_km=10.0
        )

        # Mock quota check - user has quota available
        mock_quota_service.check_quota_available.return_value = (True, 2)

        # Mock card search result
        mock_card = Card(
            id=card_id,
            owner_id=owner_id,
            idol="IU",
            idol_group="Solo",
            album="Lilac",
            status=Card.STATUS_AVAILABLE,
        )
        mock_card_repository.find_nearby_cards.return_value = [
            (mock_card, 5.2, "TestUser")
        ]

        # Act
        results = await use_case.execute(request, is_premium=False)

        # Assert
        assert len(results) == 1
        assert results[0].card_id == card_id
        assert results[0].owner_id == owner_id
        assert results[0].distance_km == 5.2
        assert results[0].idol == "IU"
        assert results[0].owner_nickname == "TestUser"

        # Verify quota was checked and incremented
        mock_quota_service.check_quota_available.assert_called_once_with(
            user_id, settings.DAILY_SEARCH_LIMIT_FREE, is_premium=False
        )
        mock_quota_service.increment_count.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_search_success_premium_user(
        self, use_case, mock_card_repository, mock_quota_service
    ):
        """Test successful search for premium user (no quota check)"""
        # Arrange
        user_id = uuid4()
        request = SearchNearbyRequest(
            user_id=user_id, lat=25.0330, lng=121.5654, radius_km=10.0
        )

        mock_card_repository.find_nearby_cards.return_value = []

        # Act
        results = await use_case.execute(request, is_premium=True)

        # Assert
        assert len(results) == 0

        # Verify quota was NOT checked or incremented for premium user
        mock_quota_service.check_quota_available.assert_not_called()
        mock_quota_service.increment_count.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_rate_limit_exceeded(
        self, use_case, mock_card_repository, mock_quota_service
    ):
        """Test rate limit exceeded for free user"""
        # Arrange
        user_id = uuid4()
        request = SearchNearbyRequest(
            user_id=user_id, lat=25.0330, lng=121.5654, radius_km=10.0
        )

        # Mock quota check - user has exhausted quota
        mock_quota_service.check_quota_available.return_value = (
            False,
            settings.DAILY_SEARCH_LIMIT_FREE,
        )

        # Act & Assert
        with pytest.raises(RateLimitExceededException) as exc_info:
            await use_case.execute(request, is_premium=False)

        assert exc_info.value.current_count == settings.DAILY_SEARCH_LIMIT_FREE
        assert exc_info.value.limit == settings.DAILY_SEARCH_LIMIT_FREE

        # Verify search was not performed
        mock_card_repository.find_nearby_cards.assert_not_called()

        # Verify quota was not incremented
        mock_quota_service.increment_count.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_invalid_latitude(self, use_case):
        """Test search with invalid latitude"""
        # Arrange
        user_id = uuid4()
        request = SearchNearbyRequest(
            user_id=user_id, lat=91.0, lng=121.5654, radius_km=10.0
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            await use_case.execute(request, is_premium=False)

    @pytest.mark.asyncio
    async def test_search_invalid_longitude(self, use_case):
        """Test search with invalid longitude"""
        # Arrange
        user_id = uuid4()
        request = SearchNearbyRequest(
            user_id=user_id, lat=25.0330, lng=181.0, radius_km=10.0
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            await use_case.execute(request, is_premium=False)

    @pytest.mark.asyncio
    async def test_search_invalid_radius(self, use_case):
        """Test search with invalid radius"""
        # Arrange
        user_id = uuid4()
        request = SearchNearbyRequest(
            user_id=user_id, lat=25.0330, lng=121.5654, radius_km=-5.0
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Radius must be positive"):
            await use_case.execute(request, is_premium=False)

    @pytest.mark.asyncio
    async def test_search_uses_default_radius(
        self, use_case, mock_card_repository, mock_quota_service
    ):
        """Test that default radius from config is used when not provided"""
        # Arrange
        user_id = uuid4()
        request = SearchNearbyRequest(
            user_id=user_id, lat=25.0330, lng=121.5654, radius_km=None
        )

        mock_quota_service.check_quota_available.return_value = (True, 0)
        mock_card_repository.find_nearby_cards.return_value = []

        # Act
        await use_case.execute(request, is_premium=False)

        # Assert - verify repository was called with default radius
        mock_card_repository.find_nearby_cards.assert_called_once()
        call_args = mock_card_repository.find_nearby_cards.call_args
        assert call_args.kwargs["radius_km"] == settings.SEARCH_RADIUS_KM

    @pytest.mark.asyncio
    async def test_search_sorts_by_distance(
        self, use_case, mock_card_repository, mock_quota_service
    ):
        """Test that results are sorted by distance"""
        # Arrange
        user_id = uuid4()
        request = SearchNearbyRequest(
            user_id=user_id, lat=25.0330, lng=121.5654, radius_km=10.0
        )

        mock_quota_service.check_quota_available.return_value = (True, 0)

        # Mock multiple cards at different distances (already sorted by repository)
        card1 = Card(id=uuid4(), owner_id=uuid4(), status=Card.STATUS_AVAILABLE)
        card2 = Card(id=uuid4(), owner_id=uuid4(), status=Card.STATUS_AVAILABLE)
        card3 = Card(id=uuid4(), owner_id=uuid4(), status=Card.STATUS_AVAILABLE)

        mock_card_repository.find_nearby_cards.return_value = [
            (card1, 2.5, "User1"),
            (card2, 5.0, "User2"),
            (card3, 7.8, "User3"),
        ]

        # Act
        results = await use_case.execute(request, is_premium=False)

        # Assert - results should maintain sorted order
        assert len(results) == 3
        assert results[0].distance_km == 2.5
        assert results[1].distance_km == 5.0
        assert results[2].distance_km == 7.8

    @pytest.mark.asyncio
    async def test_search_rounds_distance(
        self, use_case, mock_card_repository, mock_quota_service
    ):
        """Test that distance is rounded to 2 decimal places"""
        # Arrange
        user_id = uuid4()
        request = SearchNearbyRequest(
            user_id=user_id, lat=25.0330, lng=121.5654, radius_km=10.0
        )

        mock_quota_service.check_quota_available.return_value = (True, 0)

        card = Card(id=uuid4(), owner_id=uuid4(), status=Card.STATUS_AVAILABLE)
        mock_card_repository.find_nearby_cards.return_value = [
            (card, 2.56789, "User1")
        ]

        # Act
        results = await use_case.execute(request, is_premium=False)

        # Assert
        assert results[0].distance_km == 2.57  # Rounded to 2 decimal places
