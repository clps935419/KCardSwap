"""
Unit tests for ExpressInterestUseCase

Tests the express interest use case implementation with mocked repositories.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.posts.application.use_cases.express_interest_use_case import (
    ExpressInterestUseCase,
)
from app.modules.posts.domain.entities.post import Post, PostStatus


class TestExpressInterestUseCase:
    """Test ExpressInterestUseCase"""

    @pytest.fixture
    def mock_post_repository(self):
        """Create mock post repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_post_interest_repository(self):
        """Create mock post interest repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_post_repository, mock_post_interest_repository):
        """Create use case instance"""
        return ExpressInterestUseCase(
            post_repository=mock_post_repository,
            post_interest_repository=mock_post_interest_repository,
        )

    @pytest.fixture
    def sample_open_post(self):
        """Create a sample open post"""
        return Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            city_code="TPE",
            title="Test Post",
            content="Test content",
            status=PostStatus.OPEN,
            expires_at=datetime.utcnow() + timedelta(days=14),
            created_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_express_interest_success(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_open_post,
    ):
        """Test successful interest expression"""
        # Arrange
        post_id = sample_open_post.id
        user_id = str(uuid4())

        mock_post_repository.get_by_id.return_value = sample_open_post
        mock_post_interest_repository.get_by_post_and_user.return_value = None

        # Mock interest creation
        def create_side_effect(interest):
            return interest

        mock_post_interest_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(post_id=post_id, user_id=user_id)

        # Assert
        assert result is not None
        assert result.post_id == post_id
        assert result.user_id == user_id
        mock_post_interest_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_express_interest_post_not_found(
        self, use_case, mock_post_repository, mock_post_interest_repository
    ):
        """Test interest expression fails when post not found"""
        # Arrange
        post_id = str(uuid4())
        user_id = str(uuid4())

        mock_post_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Post not found"):
            await use_case.execute(post_id=post_id, user_id=user_id)

        mock_post_interest_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_express_interest_own_post(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_open_post,
    ):
        """Test cannot express interest in own post"""
        # Arrange
        post_id = sample_open_post.id
        user_id = sample_open_post.owner_id  # Same as owner

        mock_post_repository.get_by_id.return_value = sample_open_post

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot express interest in your own post"):
            await use_case.execute(post_id=post_id, user_id=user_id)

        mock_post_interest_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_express_interest_closed_post(
        self, use_case, mock_post_repository, mock_post_interest_repository
    ):
        """Test cannot express interest in closed post"""
        # Arrange
        closed_post = Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            city_code="TPE",
            title="Test Post",
            content="Test content",
            status=PostStatus.CLOSED,
            expires_at=datetime.utcnow() + timedelta(days=14),
            created_at=datetime.utcnow(),
        )
        user_id = str(uuid4())

        mock_post_repository.get_by_id.return_value = closed_post

        # Act & Assert
        with pytest.raises(ValueError, match="This post is no longer accepting interests"):
            await use_case.execute(post_id=closed_post.id, user_id=user_id)

        mock_post_interest_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_express_interest_expired_post(
        self, use_case, mock_post_repository, mock_post_interest_repository
    ):
        """Test cannot express interest in expired post"""
        # Arrange
        expired_post = Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            city_code="TPE",
            title="Test Post",
            content="Test content",
            status=PostStatus.OPEN,
            expires_at=datetime.utcnow() - timedelta(days=1),  # Expired
            created_at=datetime.utcnow(),
        )
        user_id = str(uuid4())

        mock_post_repository.get_by_id.return_value = expired_post

        # Act & Assert
        with pytest.raises(ValueError, match="This post is no longer accepting interests"):
            await use_case.execute(post_id=expired_post.id, user_id=user_id)

        mock_post_interest_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_express_interest_duplicate(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_open_post,
    ):
        """Test cannot express interest twice in same post"""
        # Arrange
        post_id = sample_open_post.id
        user_id = str(uuid4())

        mock_post_repository.get_by_id.return_value = sample_open_post

        # Mock existing interest
        existing_interest = AsyncMock()
        mock_post_interest_repository.get_by_post_and_user.return_value = existing_interest

        # Act & Assert
        with pytest.raises(
            ValueError, match="You have already expressed interest in this post"
        ):
            await use_case.execute(post_id=post_id, user_id=user_id)

        mock_post_interest_repository.create.assert_not_called()
