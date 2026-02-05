"""
Unit tests for ListBoardPostsUseCase

Tests the list board posts use case implementation with mocked repositories.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.posts.application.use_cases.list_board_posts_use_case import (
    ListBoardPostsUseCase,
)
from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.entities.post_enums import PostCategory, PostScope


class TestListBoardPostsUseCase:
    """Test ListBoardPostsUseCase"""

    @pytest.fixture
    def mock_post_repository(self):
        """Create mock post repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_post_repository):
        """Create use case instance"""
        return ListBoardPostsUseCase(post_repository=mock_post_repository)

    def _create_test_post(
        self,
        city_code: str = "TPE",
        idol: str = None,
        idol_group: str = None,
        expires_at: datetime = None,
    ) -> Post:
        """Helper to create a test post"""
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=14)

        return Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            city_code=city_code,
            title="Test Post",
            content="Test content",
            idol=idol,
            idol_group=idol_group,
            status=PostStatus.OPEN,
            scope=PostScope.CITY,
            category=PostCategory.TRADE,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.mark.asyncio
    async def test_list_posts_success(self, use_case, mock_post_repository):
        """Test successfully listing posts for a city"""
        # Arrange
        city_code = "TPE"
        posts = [
            self._create_test_post(city_code=city_code),
            self._create_test_post(city_code=city_code),
        ]
        mock_post_repository.list_by_city.return_value = posts

        # Act
        result = await use_case.execute(city_code=city_code)

        # Assert
        assert len(result) == 2
        mock_post_repository.list_by_city.assert_called_once_with(
            city_code=city_code,
            status=PostStatus.OPEN,
            idol=None,
            idol_group=None,
            limit=50,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_posts_filters_expired(self, use_case, mock_post_repository):
        """Test that expired posts are filtered out"""
        # Arrange
        city_code = "TPE"
        valid_post = self._create_test_post(
            city_code=city_code,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        expired_post = self._create_test_post(
            city_code=city_code,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        mock_post_repository.list_by_city.return_value = [valid_post, expired_post]

        # Act
        result = await use_case.execute(city_code=city_code)

        # Assert
        assert len(result) == 1
        assert result[0].id == valid_post.id

    @pytest.mark.asyncio
    async def test_list_posts_with_idol_filter(self, use_case, mock_post_repository):
        """Test listing posts with idol filter"""
        # Arrange
        city_code = "TPE"
        idol = "IU"
        posts = [self._create_test_post(city_code=city_code, idol=idol)]
        mock_post_repository.list_by_city.return_value = posts

        # Act
        result = await use_case.execute(city_code=city_code, idol=idol)

        # Assert
        assert len(result) == 1
        mock_post_repository.list_by_city.assert_called_once_with(
            city_code=city_code,
            status=PostStatus.OPEN,
            idol=idol,
            idol_group=None,
            limit=50,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_posts_with_idol_group_filter(
        self, use_case, mock_post_repository
    ):
        """Test listing posts with idol group filter"""
        # Arrange
        city_code = "TPE"
        idol_group = "BTS"
        posts = [self._create_test_post(city_code=city_code, idol_group=idol_group)]
        mock_post_repository.list_by_city.return_value = posts

        # Act
        result = await use_case.execute(city_code=city_code, idol_group=idol_group)

        # Assert
        assert len(result) == 1
        mock_post_repository.list_by_city.assert_called_once_with(
            city_code=city_code,
            status=PostStatus.OPEN,
            idol=None,
            idol_group=idol_group,
            limit=50,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_posts_with_pagination(self, use_case, mock_post_repository):
        """Test listing posts with pagination parameters"""
        # Arrange
        city_code = "TPE"
        limit = 10
        offset = 20
        posts = [self._create_test_post(city_code=city_code)]
        mock_post_repository.list_by_city.return_value = posts

        # Act
        result = await use_case.execute(city_code=city_code, limit=limit, offset=offset)

        # Assert
        assert len(result) == 1
        mock_post_repository.list_by_city.assert_called_once_with(
            city_code=city_code,
            status=PostStatus.OPEN,
            idol=None,
            idol_group=None,
            limit=limit,
            offset=offset,
        )

    @pytest.mark.asyncio
    async def test_list_posts_missing_city_code(self, use_case, mock_post_repository):
        """Test listing posts without city code fails"""
        # Act & Assert
        with pytest.raises(ValueError, match="City code is required"):
            await use_case.execute(city_code="")

        mock_post_repository.list_by_city.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_posts_empty_result(self, use_case, mock_post_repository):
        """Test listing posts returns empty list when no posts found"""
        # Arrange
        city_code = "TPE"
        mock_post_repository.list_by_city.return_value = []

        # Act
        result = await use_case.execute(city_code=city_code)

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_list_posts_only_open_status(self, use_case, mock_post_repository):
        """Test that only OPEN posts are requested from repository"""
        # Arrange
        city_code = "TPE"
        mock_post_repository.list_by_city.return_value = []

        # Act
        await use_case.execute(city_code=city_code)

        # Assert
        call_args = mock_post_repository.list_by_city.call_args
        assert call_args.kwargs["status"] == PostStatus.OPEN
