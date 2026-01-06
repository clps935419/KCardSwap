"""
Integration tests for Rating Flow

Tests the complete rating flow end-to-end including:
1. Rating a user after a successful trade
2. Getting ratings for a user
3. Getting average rating
4. Validation and business rules
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.domain.entities.rating import Rating
from app.modules.social.domain.entities.trade import Trade
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestRatingFlowIntegration:
    """Integration tests for rating flow"""

    @pytest.fixture
    def test_user_ids(self):
        """Generate test user IDs"""
        return {
            "rater": uuid4(),
            "rated": uuid4(),
        }

    @pytest.fixture
    def test_friendship(self, test_user_ids):
        """Generate test friendship"""
        return Friendship(
            id=str(uuid4()),
            user_id=str(test_user_ids["rater"]),
            friend_id=str(test_user_ids["rated"]),
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def test_trade(self, test_user_ids):
        """Generate test trade"""
        now = datetime.utcnow()
        return Trade(
            id=uuid4(),
            initiator_id=test_user_ids["rater"],
            responder_id=test_user_ids["rated"],
            status=Trade.STATUS_COMPLETED,
            created_at=now,
            completed_at=now,
            initiator_confirmed_at=now,
            responder_confirmed_at=now,
        )

    @pytest.fixture
    def test_rating(self, test_user_ids):
        """Generate test rating"""
        return Rating(
            id=str(uuid4()),
            rater_id=str(test_user_ids["rater"]),
            rated_user_id=str(test_user_ids["rated"]),
            score=5,
            comment="Great trader!",
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def mock_auth_rater(self, test_user_ids):
        """Mock authentication for rater using dependency override"""
        async def override_get_current_user_id() -> UUID:
            return test_user_ids["rater"]
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield test_user_ids["rater"]
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session using dependency override"""
        mock_session = Mock()
        
        async def override_get_db_session():
            return mock_session
        
        app.dependency_overrides[get_db_session] = override_get_db_session
        yield mock_session
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_rate_user_score_out_of_range_fails(
        self, mock_auth_rater, mock_db_session, test_user_ids
    ):
        """Test rating with score out of range fails"""
        # Act - score too low
        response = client.post(
            "/api/v1/ratings",
            json={
                "rated_user_id": str(test_user_ids["rated"]),
                "score": 0,
                "comment": "Bad",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Act - score too high
        response = client.post(
            "/api/v1/ratings",
            json={
                "rated_user_id": str(test_user_ids["rated"]),
                "score": 6,
                "comment": "Too good",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_get_user_ratings_success(
        self, mock_auth_rater, mock_db_session, test_user_ids, test_rating
    ):
        """Test successfully getting ratings for a user"""
        # Arrange
        from app.modules.social.infrastructure.repositories.rating_repository_impl import (
            RatingRepositoryImpl,
        )

        with patch.object(
            RatingRepositoryImpl, "find_by_rated_user", new_callable=AsyncMock
        ) as mock_find:
            mock_find.return_value = [test_rating]

            # Act
            response = client.get(f"/api/v1/ratings/user/{test_user_ids['rated']}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert "ratings" in data
            assert len(data["ratings"]) == 1
            assert data["ratings"][0]["score"] == 5

    @pytest.mark.asyncio
    async def test_get_average_rating_success(
        self, mock_auth_rater, mock_db_session, test_user_ids
    ):
        """Test successfully getting average rating"""
        # Arrange
        from app.modules.social.infrastructure.repositories.rating_repository_impl import (
            RatingRepositoryImpl,
        )

        with patch.object(
            RatingRepositoryImpl, "get_average_rating", new_callable=AsyncMock
        ) as mock_avg:
            mock_avg.return_value = {"average": 4.5, "count": 10}

            # Act
            response = client.get(
                f"/api/v1/ratings/user/{test_user_ids['rated']}/average"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert data["average_score"] == 4.5  # Router returns average_score
            assert data["total_ratings"] == 10  # Router returns total_ratings

    @pytest.mark.asyncio
    async def test_get_average_rating_no_ratings(
        self, mock_auth_rater, mock_db_session, test_user_ids
    ):
        """Test getting average rating when user has no ratings"""
        # Arrange
        from app.modules.social.infrastructure.repositories.rating_repository_impl import (
            RatingRepositoryImpl,
        )

        with patch.object(
            RatingRepositoryImpl, "get_average_rating", new_callable=AsyncMock
        ) as mock_avg:
            mock_avg.return_value = None

            # Act
            response = client.get(
                f"/api/v1/ratings/user/{test_user_ids['rated']}/average"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert data["average_score"] == 0.0  # Router returns average_score
            assert data["total_ratings"] == 0  # Router returns total_ratings
