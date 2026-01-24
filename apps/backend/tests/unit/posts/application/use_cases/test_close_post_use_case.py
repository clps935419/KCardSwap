"""
Unit tests for ClosePostUseCase

Tests the close post use case implementation with mocked repositories.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.posts.application.use_cases.close_post_use_case import ClosePostUseCase
from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.entities.post_enums import PostCategory, PostScope


class TestClosePostUseCase:
    """Test ClosePostUseCase"""

    @pytest.fixture
    def mock_post_repository(self):
        """Create mock post repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_post_repository):
        """Create use case instance"""
        return ClosePostUseCase(post_repository=mock_post_repository)

    @pytest.fixture
    def sample_open_post(self):
        """Create a sample open post"""
        return Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            title="Test Post",
            content="Test content",
            status=PostStatus.OPEN,
            scope=PostScope.CITY,
            category=PostCategory.TRADE,
            expires_at=datetime.utcnow() + timedelta(days=14),
            city_code="TPE",
            created_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_close_post_success(
        self, use_case, mock_post_repository, sample_open_post
    ):
        """Test successful post closing"""
        # Arrange
        post_id = sample_open_post.id
        owner_id = sample_open_post.owner_id

        mock_post_repository.get_by_id.return_value = sample_open_post
        mock_post_repository.update = AsyncMock()

        # Act
        await use_case.execute(post_id=post_id, current_user_id=owner_id)

        # Assert
        mock_post_repository.update.assert_called_once()
        assert sample_open_post.status == PostStatus.CLOSED

    @pytest.mark.asyncio
    async def test_close_post_not_found(self, use_case, mock_post_repository):
        """Test closing fails when post not found"""
        # Arrange
        post_id = str(uuid4())
        user_id = str(uuid4())

        mock_post_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Post not found"):
            await use_case.execute(post_id=post_id, current_user_id=user_id)

        mock_post_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_post_not_owner(
        self, use_case, mock_post_repository, sample_open_post
    ):
        """Test only owner can close post"""
        # Arrange
        post_id = sample_open_post.id
        non_owner_id = str(uuid4())  # Different from owner

        mock_post_repository.get_by_id.return_value = sample_open_post

        # Act & Assert
        with pytest.raises(ValueError, match="Only post owner can close the post"):
            await use_case.execute(post_id=post_id, current_user_id=non_owner_id)

        mock_post_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_post_already_closed(self, use_case, mock_post_repository):
        """Test cannot close already closed post"""
        # Arrange
        closed_post = Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            title="Test Post",
            content="Test content",
            status=PostStatus.CLOSED,
            scope=PostScope.CITY,
            category=PostCategory.TRADE,
            expires_at=datetime.utcnow() + timedelta(days=14),
            city_code="TPE",
            created_at=datetime.utcnow(),
        )

        mock_post_repository.get_by_id.return_value = closed_post

        # Act & Assert
        with pytest.raises(ValueError, match="Post is already"):
            await use_case.execute(
                post_id=closed_post.id, current_user_id=closed_post.owner_id
            )

        mock_post_repository.update.assert_not_called()


class TestAcceptInterestUseCase:
    """Test AcceptInterestUseCase - basic tests"""

    # Note: Full testing would require mocking friendship and chat room repositories
    # This is a simplified version showing the test structure
    pass


class TestRejectInterestUseCase:
    """Test RejectInterestUseCase - basic tests"""

    # Note: Similar structure to accept interest
    pass
