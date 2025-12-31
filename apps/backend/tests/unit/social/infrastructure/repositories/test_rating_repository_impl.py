"""
Unit tests for RatingRepositoryImpl

Tests the rating repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.rating import Rating
from app.modules.social.infrastructure.database.models.rating_model import RatingModel
from app.modules.social.infrastructure.repositories.rating_repository_impl import (
    RatingRepositoryImpl,
)


class TestRatingRepositoryImpl:
    """Test RatingRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return RatingRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_rating(self):
        """Create sample Rating entity"""
        return Rating(
            id=str(uuid4()),
            trade_id=str(uuid4()),
            rater_id=str(uuid4()),
            rated_user_id=str(uuid4()),
            score=5,
            comment="Great trade!",
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_rating_model(self, sample_rating):
        """Create sample RatingModel"""
        return RatingModel(
            id=UUID(sample_rating.id),
            trade_id=UUID(sample_rating.trade_id),
            rater_id=UUID(sample_rating.rater_id),
            rated_user_id=UUID(sample_rating.rated_user_id),
            score=sample_rating.score,
            comment=sample_rating.comment,
            created_at=sample_rating.created_at,
        )

    @pytest.mark.asyncio
    async def test_create_rating(self, repository, mock_session, sample_rating):
        """Test creating a rating"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_rating)

        # Assert
        assert result is not None
        assert result.id == sample_rating.id
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_rating_model):
        """Test getting rating by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_rating_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(sample_rating_model.id))

        # Assert
        assert result is not None
        assert result.id == str(sample_rating_model.id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting rating by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_trade_id(self, repository, mock_session):
        """Test getting ratings by trade ID"""
        # Arrange
        trade_id = str(uuid4())
        rating_models = [
            RatingModel(
                id=uuid4(),
                trade_id=UUID(trade_id),
                rater_id=uuid4(),
                rated_user_id=uuid4(),
                score=i + 1,
                comment=f"Comment {i}",
                created_at=datetime.utcnow(),
            )
            for i in range(2)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = rating_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_trade_id(trade_id)

        # Assert
        assert len(result) == 2
        for rating in result:
            assert rating.trade_id == trade_id

    @pytest.mark.asyncio
    async def test_get_ratings_for_user(self, repository, mock_session):
        """Test getting ratings received by a user"""
        # Arrange
        user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_ratings_for_user(user_id, limit=10)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_ratings_by_user(self, repository, mock_session):
        """Test getting ratings given by a user"""
        # Arrange
        user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_ratings_by_user(user_id, limit=10)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_rated_user(self, repository, mock_session):
        """Test finding ratings by rated user (alias method)"""
        # Arrange
        user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_rated_user(user_id, limit=20)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_average_rating(self, repository, mock_session):
        """Test getting average rating for a user"""
        # Arrange
        user_id = str(uuid4())
        expected_avg = 4.5
        expected_count = 10

        mock_result = MagicMock()
        mock_result.one.return_value = (expected_avg, expected_count)
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_average_rating(user_id)

        # Assert
        assert result is not None
        assert result["average"] == expected_avg
        assert result["count"] == expected_count

    @pytest.mark.asyncio
    async def test_get_average_rating_no_ratings(self, repository, mock_session):
        """Test getting average rating when user has no ratings"""
        # Arrange
        user_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.one.return_value = (None, 0)
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_average_rating(user_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_has_user_rated_trade_true(self, repository, mock_session):
        """Test checking if user rated trade returns True"""
        # Arrange
        rater_id = str(uuid4())
        trade_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.has_user_rated_trade(rater_id, trade_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_has_user_rated_trade_false(self, repository, mock_session):
        """Test checking if user rated trade returns False"""
        # Arrange
        rater_id = str(uuid4())
        trade_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.has_user_rated_trade(rater_id, trade_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_rating(self, repository, mock_session, sample_rating_model):
        """Test deleting a rating"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_rating_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_rating_model.id))

        # Assert
        mock_session.delete.assert_called_once()
