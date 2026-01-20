"""
Integration tests for Nearby Search Flow (Phase 5 US3)
Tests complete nearby search flow end-to-end including rate limiting
"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id

client = TestClient(app)


class TestNearbySearchIntegration:
    """Integration tests for nearby search endpoints"""

    @pytest.fixture
    def test_user_id(self):
        """Generate a test user ID"""
        return uuid4()

    @pytest.fixture
    def mock_auth_dependency(self, test_user_id):
        """Mock authentication to return a test user ID using dependency override"""
        async def override_get_current_user_id() -> UUID:
            return test_user_id

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield test_user_id
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session using dependency override"""
        # Create a mock that supports async operations
        mock_session = Mock()
        # Make execute() return an AsyncMock so it can be awaited
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        async def override_get_db_session():
            return mock_session

        app.dependency_overrides[get_db_session] = override_get_db_session
        yield mock_session
        app.dependency_overrides.clear()

    # Fixtures for mocking removed - tests now use patch.object() inside test methods
    # This ensures patches remain active during test execution

    @pytest.mark.asyncio
    async def test_search_nearby_success(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test successful nearby search"""
        # Arrange
        from app.modules.social.domain.entities.card import Card
        from app.modules.social.infrastructure.repositories.card_repository_impl import (
            CardRepositoryImpl,
        )
        from app.modules.social.infrastructure.services.search_quota_service import (
            SearchQuotaService,
        )

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

        search_payload = {"lat": 25.0330, "lng": 121.5654, "radius_km": 10.0}

        # Act & Assert with patches active during request
        with patch.object(
            CardRepositoryImpl, "find_nearby_cards", new_callable=AsyncMock
        ) as mock_find_nearby:
            with patch.object(
                SearchQuotaService, "check_quota_available", new_callable=AsyncMock
            ) as mock_check_quota:
                with patch.object(
                    SearchQuotaService, "increment_count", new_callable=AsyncMock
                ) as mock_increment:
                    # Setup mocks
                    mock_find_nearby.return_value = [
                        (mock_card1, 2.5, "User1"),
                        (mock_card2, 5.8, "User2"),
                    ]
                    mock_check_quota.return_value = (True, 2)
                    mock_increment.return_value = 3

                    # Execute request
                    response = client.post(
                        f"{settings.API_PREFIX}/nearby/search", json=search_payload
                    )

                    # Assert
                    assert response.status_code == 200
                    response_data = response.json()
                    assert "data" in response_data
                    data = response_data["data"]
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

    @pytest.mark.asyncio
    async def test_search_nearby_rate_limit_exceeded(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test rate limit exceeded returns 429"""
        # Arrange
        from app.modules.social.infrastructure.services.search_quota_service import (
            SearchQuotaService,
        )

        search_payload = {"lat": 25.0330, "lng": 121.5654, "radius_km": 10.0}

        # Act & Assert with patches active during request
        with patch.object(
            SearchQuotaService, "check_quota_available", new_callable=AsyncMock
        ) as mock_check_quota:
            # Setup mock - quota exhausted
            mock_check_quota.return_value = (False, settings.DAILY_SEARCH_LIMIT_FREE)

            # Execute request
            response = client.post(
                f"{settings.API_PREFIX}/nearby/search", json=search_payload
            )

            # Assert
            assert response.status_code == 429
            response_data = response.json()
            assert "error" in response_data
            assert "Daily search limit exceeded" in response_data["error"]["message"]

    def test_search_nearby_invalid_latitude(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test invalid latitude returns 400"""
        # Arrange
        search_payload = {"lat": 91.0, "lng": 121.5654, "radius_km": 10.0}

        # Act
        response = client.post(
            f"{settings.API_PREFIX}/nearby/search", json=search_payload
        )

        # Assert
        assert response.status_code == 400  # FastAPI returns 400 for validation errors

    def test_search_nearby_invalid_longitude(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test invalid longitude returns 400"""
        # Arrange
        search_payload = {"lat": 25.0330, "lng": 181.0, "radius_km": 10.0}

        # Act
        response = client.post(
            f"{settings.API_PREFIX}/nearby/search", json=search_payload
        )

        # Assert
        assert response.status_code == 400  # FastAPI returns 400 for validation errors

    def test_search_nearby_missing_required_fields(self, mock_auth_dependency, mock_db_session):
        """Test missing required fields returns 422"""
        # Arrange
        search_payload = {"lat": 25.0330}  # Missing lng

        # Act
        response = client.post(
            f"{settings.API_PREFIX}/nearby/search", json=search_payload
        )

        # Assert
        assert response.status_code == 400  # FastAPI returns 400 for validation errors

    @pytest.mark.asyncio
    async def test_search_nearby_optional_radius(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test search with optional radius parameter"""
        # Arrange
        from app.modules.social.domain.entities.card import Card
        from app.modules.social.infrastructure.repositories.card_repository_impl import (
            CardRepositoryImpl,
        )
        from app.modules.social.infrastructure.services.search_quota_service import (
            SearchQuotaService,
        )

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

        search_payload = {"lat": 25.0330, "lng": 121.5654}  # No radius

        # Act & Assert with patches active during request
        with patch.object(
            CardRepositoryImpl, "find_nearby_cards", new_callable=AsyncMock
        ) as mock_find_nearby:
            with patch.object(
                SearchQuotaService, "check_quota_available", new_callable=AsyncMock
            ) as mock_check_quota:
                with patch.object(
                    SearchQuotaService, "increment_count", new_callable=AsyncMock
                ) as mock_increment:
                    # Setup mocks
                    mock_find_nearby.return_value = [
                        (mock_card1, 2.5, "User1"),
                        (mock_card2, 5.8, "User2"),
                    ]
                    mock_check_quota.return_value = (True, 2)
                    mock_increment.return_value = 3

                    # Execute request
                    response = client.post(
                        f"{settings.API_PREFIX}/nearby/search", json=search_payload
                    )

                    # Assert
                    assert response.status_code == 200
                    response_data = response.json()
                    assert "data" in response_data
                    data = response_data["data"]
                    assert data["count"] == 2


class TestUpdateLocationIntegration:
    """Integration tests for location update endpoint"""

    @pytest.fixture
    def test_user_id(self):
        """Generate a test user ID"""
        return uuid4()

    @pytest.fixture
    def mock_auth_dependency(self, test_user_id):
        """Mock authentication using dependency override"""
        async def override_get_current_user_id() -> UUID:
            return test_user_id

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield test_user_id
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session using dependency override"""
        # Create a mock that supports async operations
        mock_session = Mock()
        # Make execute() return an AsyncMock so it can be awaited
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        async def override_get_db_session():
            return mock_session

        app.dependency_overrides[get_db_session] = override_get_db_session
        yield mock_session
        app.dependency_overrides.clear()

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
        response = client.put(
            f"{settings.API_PREFIX}/nearby/location", json=location_payload
        )

        # Assert
        assert response.status_code == 200  # API returns 200, not 204

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
        response = client.put(
            f"{settings.API_PREFIX}/nearby/location", json=location_payload
        )

        # Assert
        assert response.status_code == 400  # FastAPI returns 400 for validation errors

    def test_update_location_invalid_longitude(
        self,
        mock_auth_dependency,
        mock_db_session,
    ):
        """Test invalid longitude returns 400"""
        # Arrange
        location_payload = {"lat": 25.0330, "lng": 181.0}

        # Act
        response = client.put(
            f"{settings.API_PREFIX}/nearby/location", json=location_payload
        )

        # Assert
        assert response.status_code == 400  # FastAPI returns 400 for validation errors

    def test_update_location_missing_fields(self, mock_auth_dependency, mock_db_session):
        """Test missing required fields returns 400"""
        # Arrange
        location_payload = {"lat": 25.0330}  # Missing lng

        # Act
        response = client.put(
            f"{settings.API_PREFIX}/nearby/location", json=location_payload
        )

        # Assert
        assert response.status_code == 400  # FastAPI returns 400 for validation errors
