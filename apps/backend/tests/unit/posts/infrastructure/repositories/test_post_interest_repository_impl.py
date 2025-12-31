"""
Unit tests for PostInterestRepositoryImpl

Tests the post interest repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.domain.entities.post_interest import (
    PostInterest,
    PostInterestStatus,
)
from app.modules.posts.infrastructure.database.models.post_interest_model import (
    PostInterestModel,
)
from app.modules.posts.infrastructure.repositories.post_interest_repository_impl import (
    PostInterestRepositoryImpl,
)


class TestPostInterestRepositoryImpl:
    """Test PostInterestRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return PostInterestRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_interest(self):
        """Create sample PostInterest entity"""
        return PostInterest(
            id=str(uuid4()),
            post_id=str(uuid4()),
            user_id=str(uuid4()),
            status=PostInterestStatus.PENDING,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_interest_model(self, sample_interest):
        """Create sample PostInterestModel"""
        return PostInterestModel(
            id=UUID(sample_interest.id),
            post_id=UUID(sample_interest.post_id),
            user_id=UUID(sample_interest.user_id),
            status=sample_interest.status.value,
            created_at=sample_interest.created_at,
            updated_at=sample_interest.updated_at,
        )

    @pytest.mark.asyncio
    async def test_create_interest(self, repository, mock_session, sample_interest):
        """Test creating a post interest"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_interest)

        # Assert
        assert result is not None
        assert result.id == sample_interest.id
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_interest_model):
        """Test getting interest by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_interest_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(sample_interest_model.id))

        # Assert
        assert result is not None
        assert result.id == str(sample_interest_model.id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting interest by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_post_and_user_found(self, repository, mock_session, sample_interest_model):
        """Test getting interest by post and user when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_interest_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_post_and_user(
            str(sample_interest_model.post_id), str(sample_interest_model.user_id)
        )

        # Assert
        assert result is not None
        assert result.post_id == str(sample_interest_model.post_id)
        assert result.user_id == str(sample_interest_model.user_id)

    @pytest.mark.asyncio
    async def test_get_by_post_and_user_not_found(self, repository, mock_session):
        """Test getting interest by post and user when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_post_and_user(str(uuid4()), str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_by_post_id(self, repository, mock_session):
        """Test listing interests by post ID"""
        # Arrange
        post_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.list_by_post_id(post_id)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_by_post_id_with_status_filter(self, repository, mock_session):
        """Test listing interests with status filter"""
        # Arrange
        post_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.list_by_post_id(
            post_id, status=PostInterestStatus.ACCEPTED
        )

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_by_user_id(self, repository, mock_session):
        """Test listing interests by user ID"""
        # Arrange
        user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.list_by_user_id(user_id)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_interest(
        self, repository, mock_session, sample_interest, sample_interest_model
    ):
        """Test updating a post interest"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_interest_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Modify the interest
        sample_interest.status = PostInterestStatus.ACCEPTED

        # Act
        result = await repository.update(sample_interest)

        # Assert
        assert result is not None
        assert result.id == sample_interest.id

    @pytest.mark.asyncio
    async def test_delete_interest(self, repository, mock_session, sample_interest_model):
        """Test deleting a post interest"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_interest_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_interest_model.id))

        # Assert
        mock_session.delete.assert_called_once()
