"""
Unit tests for PostRepositoryImpl

Tests the post repository implementation with mocked database session.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.infrastructure.database.models.post_model import PostModel
from app.modules.posts.infrastructure.repositories.post_repository_impl import (
    PostRepositoryImpl,
)


class TestPostRepositoryImpl:
    """Test PostRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return PostRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_post(self):
        """Create sample Post entity"""
        return Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            city_code="TPE",
            title="Looking for IU photocard",
            content="Want to exchange IU photocard for BTS",
            idol="IU",
            idol_group="Solo",
            status=PostStatus.OPEN,
            expires_at=datetime.utcnow() + timedelta(days=14),
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_post_model(self, sample_post):
        """Create sample PostModel"""
        return PostModel(
            id=UUID(sample_post.id),
            owner_id=UUID(sample_post.owner_id),
            city_code=sample_post.city_code,
            title=sample_post.title,
            content=sample_post.content,
            idol=sample_post.idol,
            idol_group=sample_post.idol_group,
            status=sample_post.status.value,
            expires_at=sample_post.expires_at,
            created_at=sample_post.created_at,
            updated_at=sample_post.updated_at,
        )

    @pytest.mark.asyncio
    async def test_create_post(self, repository, mock_session, sample_post):
        """Test creating a post"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_post)

        # Assert
        assert result is not None
        assert result.id == sample_post.id
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_post_model):
        """Test getting post by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_post_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(sample_post_model.id))

        # Assert
        assert result is not None
        assert result.id == str(sample_post_model.id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting post by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_by_city(self, repository, mock_session):
        """Test listing posts by city"""
        # Arrange
        city_code = "TPE"
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.list_by_city(city_code)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_by_city_with_filters(self, repository, mock_session):
        """Test listing posts with filters"""
        # Arrange
        city_code = "TPE"
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.list_by_city(
            city_code, status=PostStatus.OPEN, idol="IU", limit=10
        )

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_user_posts_today(self, repository, mock_session):
        """Test counting user posts today"""
        # Arrange
        user_id = str(uuid4())
        expected_count = 2

        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.count_user_posts_today(user_id)

        # Assert
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_update_post(self, repository, mock_session, sample_post, sample_post_model):
        """Test updating a post"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_post_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Modify the post
        sample_post.title = "Updated Title"

        # Act
        result = await repository.update(sample_post)

        # Assert
        assert result is not None
        assert result.id == sample_post.id

    @pytest.mark.asyncio
    async def test_delete_post(self, repository, mock_session, sample_post_model):
        """Test deleting a post"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_post_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_post_model.id))

        # Assert
        mock_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_owner_id(self, repository, mock_session):
        """Test getting posts by owner ID"""
        # Arrange
        owner_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_owner_id(owner_id)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_expired_posts(self, repository, mock_session):
        """Test marking expired posts"""
        # Arrange
        expected_count = 3
        
        # Create mock expired post models
        mock_posts = []
        for _ in range(expected_count):
            mock_post = MagicMock()
            mock_post.status = PostStatus.OPEN.value
            mock_posts.append(mock_post)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_posts
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.mark_expired_posts()

        # Assert
        assert result == expected_count
        mock_session.flush.assert_called_once()
