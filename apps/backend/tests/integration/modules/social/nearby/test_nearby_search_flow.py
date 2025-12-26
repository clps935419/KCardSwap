"""
Integration tests for Nearby Search Flow (Phase 5 US3)
Tests complete nearby search flow end-to-end including rate limiting
"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


class TestNearbySearchIntegration:
    """Integration tests for nearby search endpoints"""

    @pytest.fixture
    def test_user_id(self):
        """Generate a test user ID"""
        return uuid4()

    @pytest.fixture
    def mock_auth_dependency(self, test_user_id):
        """Mock authentication to return a test user ID"""

        async def mock_get_current_user_id():
            return test_user_id

        with patch(
            "app.modules.social.presentation.routers.nearby_router.get_current_user_id",
            return_value=test_user_id,
        ):
            yield test_user_id

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        with patch(
            "app.modules.social.presentation.routers.nearby_router.get_db_session"
        ) as mock:
            session = Mock()
            mock.return_value = session
            yield session

    @pytest.fixture
    def mock_card_repository_with_results(self):
        """Mock card repository with nearby cards"""
        from app.modules.social.domain.entities.card import Card

        with patch(
            "app.modules.social.infrastructure.repositories.card_repository_impl.CardRepositoryImpl"
        ) as mock:
            repo_instance = Mock()

            # Create mock cards
            card1_id = uuid4()
            owner1_id = uuid4()
            mock_card1 = Card(
                id=card1_id,
                owner_id=owner1_id,
                idol="IU",
                idol_group="Solo",
                album="Lilac",
                status=Card.STATUS_AVAILABLE,
            )

            card2_id = uuid4()
            owner2_id = uuid4()
            mock_card2 = Card(
                id=card2_id,
                owner_id=owner2_id,
                idol="Jennie",
                idol_group="BLACKPINK",
                album="SOLO",
                rarity=Card.RARITY_RARE,
                status=Card.STATUS_AVAILABLE,
            )

            # Mock find_nearby_cards to return these cards
            repo_instance.find_nearby_cards = AsyncMock(
                return_value=[
                    (mock_card1, 2.5, "User1"),
                    (mock_card2, 5.8, "User2"),
                ]
            )

            mock.return_value = repo_instance
            yield repo_instance

    @pytest.fixture
    def mock_quota_service_available(self):
        """Mock quota service with quota available"""
        with patch(
            "app.modules.social.infrastructure.services.search_quota_service.SearchQuotaService"
        ) as mock:
            service = Mock()
            service.check_quota_available = AsyncMock(return_value=(True, 2))
            service.increment_count = AsyncMock(return_value=3)
            mock.return_value = service
            yield service

    @pytest.fixture
    def mock_quota_service_exhausted(self):
        """Mock quota service with quota exhausted"""
        with patch(
            "app.modules.social.infrastructure.services.search_quota_service.SearchQuotaService"
        ) as mock:
            service = Mock()
            service.check_quota_available = AsyncMock(
                return_value=(False, settings.DAILY_SEARCH_LIMIT_FREE)
            )
            mock.return_value = service
            yield service

    def test_search_nearby_success(
        self,
        mock_auth_dependency,
        mock_db_session,
        mock_card_repository_with_results,
        mock_quota_service_available,
    ):
        """Test successful nearby search"""
        # Arrange
        search_payload = {"lat": 25.0330, "lng": 121.5654, "radius_km": 10.0}

        # Act
        response = client.post(f"{settings.API_PREFIX}/nearby/search", json=search_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["results"]) == 2

        # Check first result
        result1 = data["results"][0]
        assert result1["distance_km"] == 2.5
        assert result1["idol"] == "IU"
        assert result1["owner_nickname"] == "User1"

        # Check second result
        result2 = data["results"][1]
        assert result2["distance_km"] == 5.8
        assert result2["idol"] == "Jennie"
        assert result2["idol_group"] == "BLACKPINK"

    def test_search_nearby_rate_limit_exceeded(
        self,
        mock_auth_dependency,
        mock_db_session,
        mock_card_repository_with_results,
        mock_quota_service_exhausted,
    ):
        """Test rate limit exceeded returns 429"""
        # Arrange
        search_payload = {"lat": 25.0330, "lng": 121.5654, "radius_km": 10.0}

        # Act
        response = client.post(f"{settings.API_PREFIX}/nearby/search", json=search_payload)

        # Assert
        assert response.status_code == 429
        data = response.json()
        assert "detail" in data
        assert "Daily search limit exceeded" in data["detail"]

    def test_search_nearby_invalid_latitude(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test invalid latitude returns 400"""
        # Arrange
        search_payload = {"lat": 91.0, "lng": 121.5654, "radius_km": 10.0}

        # Act
        response = client.post(f"{settings.API_PREFIX}/nearby/search", json=search_payload)

        # Assert
        assert response.status_code == 422  # Pydantic validation error

    def test_search_nearby_invalid_longitude(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test invalid longitude returns 400"""
        # Arrange
        search_payload = {"lat": 25.0330, "lng": 181.0, "radius_km": 10.0}

        # Act
        response = client.post(f"{settings.API_PREFIX}/nearby/search", json=search_payload)

        # Assert
        assert response.status_code == 422  # Pydantic validation error

    def test_search_nearby_missing_required_fields(self):
        """Test missing required fields returns 422"""
        # Arrange
        search_payload = {"lat": 25.0330}  # Missing lng

        # Act
        response = client.post(f"{settings.API_PREFIX}/nearby/search", json=search_payload)

        # Assert
        assert response.status_code == 422

    def test_search_nearby_optional_radius(
        self,
        mock_auth_dependency,
        mock_db_session,
        mock_card_repository_with_results,
        mock_quota_service_available,
    ):
        """Test search with optional radius parameter"""
        # Arrange
        search_payload = {"lat": 25.0330, "lng": 121.5654}  # No radius

        # Act
        response = client.post(f"{settings.API_PREFIX}/nearby/search", json=search_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2


class TestUpdateLocationIntegration:
    """Integration tests for location update endpoint"""

    @pytest.fixture
    def test_user_id(self):
        """Generate a test user ID"""
        return uuid4()

    @pytest.fixture
    def mock_auth_dependency(self, test_user_id):
        """Mock authentication"""

        async def mock_get_current_user_id():
            return test_user_id

        with patch(
            "app.modules.social.presentation.routers.nearby_router.get_current_user_id",
            return_value=test_user_id,
        ):
            yield test_user_id

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        with patch(
            "app.modules.social.presentation.routers.nearby_router.get_db_session"
        ) as mock:
            session = Mock()
            mock.return_value = session
            yield session

    @pytest.fixture
    def mock_profile_repository(self):
        """Mock profile repository"""
        from app.modules.identity.domain.entities.profile import Profile

        with patch(
            "app.modules.identity.infrastructure.repositories.profile_repository_impl.ProfileRepositoryImpl"
        ) as mock:
            repo_instance = Mock()

            # Create mock profile
            test_profile = Profile(
                user_id=uuid4(),
                nickname="TestUser",
                last_lat=None,
                last_lng=None,
            )

            repo_instance.get_by_user_id = AsyncMock(return_value=test_profile)
            repo_instance.save = AsyncMock(return_value=test_profile)

            mock.return_value = repo_instance
            yield repo_instance

    def test_update_location_success(
        self,
        mock_auth_dependency,
        mock_db_session,
        mock_profile_repository,
    ):
        """Test successful location update"""
        # Arrange
        location_payload = {"lat": 25.0330, "lng": 121.5654}

        # Act
        response = client.put(f"{settings.API_PREFIX}/nearby/location", json=location_payload)

        # Assert
        assert response.status_code == 204

        # Verify profile repository was called
        mock_profile_repository.get_by_user_id.assert_called_once()
        mock_profile_repository.save.assert_called_once()

    def test_update_location_invalid_latitude(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test invalid latitude returns 422"""
        # Arrange
        location_payload = {"lat": 91.0, "lng": 121.5654}

        # Act
        response = client.put(f"{settings.API_PREFIX}/nearby/location", json=location_payload)

        # Assert
        assert response.status_code == 422

    def test_update_location_invalid_longitude(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test invalid longitude returns 422"""
        # Arrange
        location_payload = {"lat": 25.0330, "lng": 181.0}

        # Act
        response = client.put(f"{settings.API_PREFIX}/nearby/location", json=location_payload)

        # Assert
        assert response.status_code == 422

    def test_update_location_missing_fields(self):
        """Test missing required fields returns 422"""
        # Arrange
        location_payload = {"lat": 25.0330}  # Missing lng

        # Act
        response = client.put(f"{settings.API_PREFIX}/nearby/location", json=location_payload)

        # Assert
        assert response.status_code == 422
