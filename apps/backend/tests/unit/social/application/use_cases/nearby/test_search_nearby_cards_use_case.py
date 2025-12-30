"""
Unit tests for SearchNearbyCardsUseCase
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.config import settings
from app.modules.social.application.dtos.nearby_dtos import (
    NearbyCardResult,
    SearchNearbyRequest,
)
from app.modules.social.application.use_cases.nearby.search_nearby_cards_use_case import (
    RateLimitExceededException,
    SearchNearbyCardsUseCase,
)


class TestRateLimitExceededException:
    """Test RateLimitExceededException"""

    def test_rate_limit_exception_creation(self):
        """Test creating RateLimitExceededException"""
        # Arrange & Act
        exception = RateLimitExceededException(current_count=5, limit=5)

        # Assert
        assert exception.current_count == 5
        assert exception.limit == 5
        assert "Daily search limit exceeded" in str(exception)
        assert "5/5 searches used" in str(exception)

    def test_rate_limit_exception_message(self):
        """Test exception message format"""
        # Arrange & Act
        exception = RateLimitExceededException(current_count=3, limit=5)

        # Assert
        assert str(exception) == "Daily search limit exceeded: 3/5 searches used"


class TestSearchNearbyCardsUseCase:
    """Test SearchNearbyCardsUseCase"""

    @pytest.fixture
    def mock_card_repository(self):
        """Create mock card repository"""
        repo = AsyncMock()
        repo.find_nearby_cards = AsyncMock(return_value=[])
        return repo

    @pytest.fixture
    def mock_quota_service(self):
        """Create mock quota service"""
        service = AsyncMock()
        service.check_quota_available = AsyncMock(return_value=(True, 0))
        service.increment_count = AsyncMock(return_value=1)
        return service

    @pytest.fixture
    def use_case(self, mock_card_repository, mock_quota_service):
        """Create use case instance"""
        return SearchNearbyCardsUseCase(
            card_repository=mock_card_repository,
            quota_service=mock_quota_service,
        )

    @pytest.fixture
    def search_request(self):
        """Create a valid search request"""
        return SearchNearbyRequest(
            user_id=uuid4(),
            lat=25.0330,
            lng=121.5654,
            radius_km=10.0,
        )

    @pytest.mark.asyncio
    async def test_search_nearby_cards_success(
        self, use_case, mock_card_repository, mock_quota_service, search_request
    ):
        """Test successful search for nearby cards"""
        # Arrange
        from app.modules.social.domain.entities.card import Card

        card1 = Card(
            id=uuid4(),
            owner_id=uuid4(),
            idol="IU",
            idol_group="Solo",
            album="Lilac",
            status=Card.STATUS_AVAILABLE,
        )
        card2 = Card(
            id=uuid4(),
            owner_id=uuid4(),
            idol="Jennie",
            idol_group="BLACKPINK",
            album="SOLO",
            status=Card.STATUS_AVAILABLE,
        )

        mock_card_repository.find_nearby_cards.return_value = [
            (card1, 2.543, "User1"),
            (card2, 5.876, "User2"),
        ]

        # Act
        results = await use_case.execute(search_request, is_premium=False)

        # Assert
        assert len(results) == 2
        assert isinstance(results[0], NearbyCardResult)
        assert results[0].card_id == card1.id
        assert results[0].distance_km == 2.54  # Rounded to 2 decimals
        assert results[0].idol == "IU"
        assert results[0].owner_nickname == "User1"

        assert results[1].card_id == card2.id
        assert results[1].distance_km == 5.88  # Rounded to 2 decimals
        assert results[1].idol == "Jennie"
        assert results[1].owner_nickname == "User2"

        # Verify quota was checked and incremented
        mock_quota_service.check_quota_available.assert_called_once_with(
            search_request.user_id, settings.DAILY_SEARCH_LIMIT_FREE, is_premium=False
        )
        mock_quota_service.increment_count.assert_called_once_with(
            search_request.user_id
        )

    @pytest.mark.asyncio
    async def test_search_nearby_cards_no_results(
        self, use_case, mock_card_repository, search_request
    ):
        """Test search with no nearby cards found"""
        # Arrange
        mock_card_repository.find_nearby_cards.return_value = []

        # Act
        results = await use_case.execute(search_request, is_premium=False)

        # Assert
        assert len(results) == 0
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_nearby_cards_premium_user_no_quota_check(
        self, use_case, mock_card_repository, mock_quota_service, search_request
    ):
        """Test premium user search does not check quota"""
        # Arrange
        mock_card_repository.find_nearby_cards.return_value = []

        # Act
        results = await use_case.execute(search_request, is_premium=True)

        # Assert
        assert len(results) == 0
        # Verify quota was NOT checked or incremented for premium users
        mock_quota_service.check_quota_available.assert_not_called()
        mock_quota_service.increment_count.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_nearby_cards_free_user_quota_available(
        self, use_case, mock_card_repository, mock_quota_service, search_request
    ):
        """Test free user with quota available"""
        # Arrange
        mock_card_repository.find_nearby_cards.return_value = []
        mock_quota_service.check_quota_available.return_value = (True, 2)

        # Act
        results = await use_case.execute(search_request, is_premium=False)

        # Assert
        assert len(results) == 0
        mock_quota_service.check_quota_available.assert_called_once()
        mock_quota_service.increment_count.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_nearby_cards_quota_exceeded(
        self, use_case, mock_quota_service, search_request
    ):
        """Test rate limit exception when quota exhausted"""
        # Arrange
        mock_quota_service.check_quota_available.return_value = (
            False,
            settings.DAILY_SEARCH_LIMIT_FREE,
        )

        # Act & Assert
        with pytest.raises(RateLimitExceededException) as exc_info:
            await use_case.execute(search_request, is_premium=False)

        # Verify exception details
        exception = exc_info.value
        assert exception.current_count == settings.DAILY_SEARCH_LIMIT_FREE
        assert exception.limit == settings.DAILY_SEARCH_LIMIT_FREE
        assert "Daily search limit exceeded" in str(exception)

        # Verify increment was NOT called when quota exceeded
        mock_quota_service.increment_count.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_nearby_cards_invalid_latitude_too_low(
        self, use_case, search_request
    ):
        """Test invalid latitude below -90"""
        # Arrange
        search_request.lat = -91.0

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(search_request, is_premium=False)

        assert "Latitude must be between -90 and 90" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_nearby_cards_invalid_latitude_too_high(
        self, use_case, search_request
    ):
        """Test invalid latitude above 90"""
        # Arrange
        search_request.lat = 91.0

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(search_request, is_premium=False)

        assert "Latitude must be between -90 and 90" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_nearby_cards_invalid_longitude_too_low(
        self, use_case, search_request
    ):
        """Test invalid longitude below -180"""
        # Arrange
        search_request.lng = -181.0

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(search_request, is_premium=False)

        assert "Longitude must be between -180 and 180" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_nearby_cards_invalid_longitude_too_high(
        self, use_case, search_request
    ):
        """Test invalid longitude above 180"""
        # Arrange
        search_request.lng = 181.0

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(search_request, is_premium=False)

        assert "Longitude must be between -180 and 180" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_nearby_cards_edge_case_valid_coordinates(
        self, use_case, mock_card_repository, search_request
    ):
        """Test edge cases for valid coordinates"""
        # Arrange
        mock_card_repository.find_nearby_cards.return_value = []

        # Test maximum valid latitude
        search_request.lat = 90.0
        search_request.lng = 180.0
        results1 = await use_case.execute(search_request, is_premium=True)
        assert len(results1) == 0

        # Test minimum valid latitude
        search_request.lat = -90.0
        search_request.lng = -180.0
        results2 = await use_case.execute(search_request, is_premium=True)
        assert len(results2) == 0

    @pytest.mark.asyncio
    async def test_search_nearby_cards_invalid_radius_negative(
        self, use_case, search_request
    ):
        """Test invalid negative radius"""
        # Arrange
        search_request.radius_km = -5.0

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(search_request, is_premium=False)

        assert "Radius must be positive" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_nearby_cards_radius_zero_uses_default(
        self, use_case, mock_card_repository, search_request
    ):
        """Test zero radius falls back to default radius"""
        # Arrange
        search_request.radius_km = 0
        mock_card_repository.find_nearby_cards.return_value = []

        # Act
        await use_case.execute(search_request, is_premium=True)

        # Assert - verify repository called with default radius when 0 provided
        mock_card_repository.find_nearby_cards.assert_called_once()
        call_args = mock_card_repository.find_nearby_cards.call_args
        assert call_args.kwargs["radius_km"] == settings.SEARCH_RADIUS_KM

    @pytest.mark.asyncio
    async def test_search_nearby_cards_default_radius(
        self, use_case, mock_card_repository, search_request
    ):
        """Test using default radius when not provided"""
        # Arrange
        search_request.radius_km = None
        mock_card_repository.find_nearby_cards.return_value = []

        # Act
        await use_case.execute(search_request, is_premium=True)

        # Assert - verify repository called with default radius from settings
        mock_card_repository.find_nearby_cards.assert_called_once()
        call_args = mock_card_repository.find_nearby_cards.call_args
        assert call_args.kwargs["radius_km"] == settings.SEARCH_RADIUS_KM

    @pytest.mark.asyncio
    async def test_search_nearby_cards_custom_radius(
        self, use_case, mock_card_repository, search_request
    ):
        """Test using custom radius"""
        # Arrange
        custom_radius = 20.0
        search_request.radius_km = custom_radius
        mock_card_repository.find_nearby_cards.return_value = []

        # Act
        await use_case.execute(search_request, is_premium=True)

        # Assert - verify repository called with custom radius
        mock_card_repository.find_nearby_cards.assert_called_once()
        call_args = mock_card_repository.find_nearby_cards.call_args
        assert call_args.kwargs["radius_km"] == custom_radius

    @pytest.mark.asyncio
    async def test_search_nearby_cards_exclude_user_and_stealth(
        self, use_case, mock_card_repository, search_request
    ):
        """Test that search excludes requesting user and stealth users"""
        # Arrange
        mock_card_repository.find_nearby_cards.return_value = []

        # Act
        await use_case.execute(search_request, is_premium=True)

        # Assert - verify repository called with correct exclusion flags
        mock_card_repository.find_nearby_cards.assert_called_once_with(
            lat=search_request.lat,
            lng=search_request.lng,
            radius_km=search_request.radius_km,
            exclude_user_id=search_request.user_id,
            exclude_stealth_users=True,
        )

    @pytest.mark.asyncio
    async def test_search_nearby_cards_distance_rounding(
        self, use_case, mock_card_repository, search_request
    ):
        """Test that distances are rounded to 2 decimal places"""
        # Arrange
        from app.modules.social.domain.entities.card import Card

        card = Card(
            id=uuid4(),
            owner_id=uuid4(),
            idol="Test",
            idol_group="Group",
            album="Album",
            status=Card.STATUS_AVAILABLE,
        )

        # Test various rounding scenarios
        test_cases = [
            (1.234567, 1.23),  # Round down
            (1.235, 1.24),  # Round up (midpoint)
            (1.999, 2.0),  # Round up
            (0.001, 0.0),  # Very small
            (10.0, 10.0),  # Exact integer
        ]

        for distance_input, expected_output in test_cases:
            mock_card_repository.find_nearby_cards.return_value = [
                (card, distance_input, "TestUser")
            ]

            # Act
            results = await use_case.execute(search_request, is_premium=True)

            # Assert
            assert len(results) == 1
            assert results[0].distance_km == expected_output

    @pytest.mark.asyncio
    async def test_search_nearby_cards_all_card_fields_mapped(
        self, use_case, mock_card_repository, search_request
    ):
        """Test that all card fields are properly mapped to NearbyCardResult"""
        # Arrange
        from app.modules.social.domain.entities.card import Card

        card_id = uuid4()
        owner_id = uuid4()
        card = Card(
            id=card_id,
            owner_id=owner_id,
            idol="IU",
            idol_group="Solo",
            album="Lilac",
            version="Ver. A",
            rarity=Card.RARITY_RARE,
            image_url="https://example.com/image.jpg",
            status=Card.STATUS_AVAILABLE,
        )

        mock_card_repository.find_nearby_cards.return_value = [
            (card, 3.5, "NicknameTest")
        ]

        # Act
        results = await use_case.execute(search_request, is_premium=True)

        # Assert
        assert len(results) == 1
        result = results[0]
        assert result.card_id == card_id
        assert result.owner_id == owner_id
        assert result.distance_km == 3.5
        assert result.idol == "IU"
        assert result.idol_group == "Solo"
        assert result.album == "Lilac"
        assert result.version == "Ver. A"
        assert result.rarity == "rare"
        assert result.image_url == "https://example.com/image.jpg"
        assert result.owner_nickname == "NicknameTest"

    @pytest.mark.asyncio
    async def test_search_nearby_cards_quota_increment_after_successful_search(
        self, use_case, mock_card_repository, mock_quota_service, search_request
    ):
        """Test that quota is incremented only after successful search"""
        # Arrange
        from app.modules.social.domain.entities.card import Card

        card = Card(
            id=uuid4(),
            owner_id=uuid4(),
            idol="Test",
            status=Card.STATUS_AVAILABLE,
        )
        mock_card_repository.find_nearby_cards.return_value = [(card, 5.0, "User")]
        mock_quota_service.check_quota_available.return_value = (True, 2)

        # Act
        await use_case.execute(search_request, is_premium=False)

        # Assert - increment should be called AFTER search completes
        assert mock_quota_service.increment_count.call_count == 1
        mock_quota_service.increment_count.assert_called_with(search_request.user_id)

    @pytest.mark.asyncio
    async def test_search_nearby_cards_multiple_cards_same_owner(
        self, use_case, mock_card_repository, search_request
    ):
        """Test search with multiple cards from the same owner"""
        # Arrange
        from app.modules.social.domain.entities.card import Card

        owner_id = uuid4()
        card1 = Card(
            id=uuid4(),
            owner_id=owner_id,
            idol="Card1",
            status=Card.STATUS_AVAILABLE,
        )
        card2 = Card(
            id=uuid4(),
            owner_id=owner_id,
            idol="Card2",
            status=Card.STATUS_AVAILABLE,
        )

        mock_card_repository.find_nearby_cards.return_value = [
            (card1, 1.5, "SameOwner"),
            (card2, 2.5, "SameOwner"),
        ]

        # Act
        results = await use_case.execute(search_request, is_premium=True)

        # Assert
        assert len(results) == 2
        assert results[0].owner_id == owner_id
        assert results[1].owner_id == owner_id
        assert results[0].owner_nickname == "SameOwner"
        assert results[1].owner_nickname == "SameOwner"
