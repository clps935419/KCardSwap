"""
Unit tests for CreatePostUseCase

Tests the create post use case implementation with mocked repositories.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.posts.application.use_cases.create_post_use_case import (
    CreatePostUseCase,
)


class TestCreatePostUseCase:
    """Test CreatePostUseCase"""

    @pytest.fixture
    def mock_post_repository(self):
        """Create mock post repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_subscription_repository(self):
        """Create mock subscription repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_post_repository, mock_subscription_repository):
        """Create use case instance"""
        return CreatePostUseCase(
            post_repository=mock_post_repository,
            subscription_repository=mock_subscription_repository,
        )

    @pytest.mark.asyncio
    async def test_create_post_success_premium_user(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test successful post creation for premium user"""
        # Arrange
        owner_id = str(uuid4())
        city_code = "TPE"
        title = "Looking for IU photocard"
        content = "Want to exchange IU photocard"

        # Mock premium subscription
        mock_subscription = AsyncMock()
        mock_subscription.is_premium.return_value = True
        mock_subscription_repository.get_by_user_id.return_value = mock_subscription

        # Mock post creation
        def create_side_effect(post):
            return post

        mock_post_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            owner_id=owner_id,
            city_code=city_code,
            title=title,
            content=content,
        )

        # Assert
        assert result is not None
        assert result.owner_id == owner_id
        assert result.city_code == city_code
        assert result.title == title
        assert result.content == content
        mock_post_repository.create.assert_called_once()
        # Premium users don't need daily limit check
        mock_post_repository.count_user_posts_today.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_post_success_free_user_under_limit(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test successful post creation for free user under daily limit"""
        # Arrange
        owner_id = str(uuid4())

        # Mock no subscription (free user)
        mock_subscription_repository.get_by_user_id.return_value = None

        # Mock user has posted once today (under limit of 2)
        mock_post_repository.count_user_posts_today.return_value = 1

        # Mock post creation
        def create_side_effect(post):
            return post

        mock_post_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            owner_id=owner_id,
            city_code="TPE",
            title="Test Post",
            content="Test content",
        )

        # Assert
        assert result is not None
        mock_post_repository.count_user_posts_today.assert_called_once_with(owner_id)
        mock_post_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_post_free_user_exceeds_daily_limit(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test post creation fails when free user exceeds daily limit"""
        # Arrange
        owner_id = str(uuid4())

        # Mock no subscription (free user)
        mock_subscription_repository.get_by_user_id.return_value = None

        # Mock user has reached daily limit
        mock_post_repository.count_user_posts_today.return_value = 2

        # Act & Assert
        with pytest.raises(ValueError, match="Daily post limit reached"):
            await use_case.execute(
                owner_id=owner_id,
                city_code="TPE",
                title="Test Post",
                content="Test content",
            )

        mock_post_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_post_missing_city_code(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test post creation fails when city code is missing"""
        # Act & Assert
        with pytest.raises(ValueError, match="City code is required"):
            await use_case.execute(
                owner_id=str(uuid4()),
                city_code="",
                title="Test Post",
                content="Test content",
            )

        mock_post_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_post_missing_title(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test post creation fails when title is missing"""
        # Act & Assert
        with pytest.raises(ValueError, match="Title is required"):
            await use_case.execute(
                owner_id=str(uuid4()),
                city_code="TPE",
                title="",
                content="Test content",
            )

        mock_post_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_post_title_too_long(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test post creation fails when title exceeds 120 characters"""
        # Arrange
        long_title = "x" * 121

        # Act & Assert
        with pytest.raises(ValueError, match="Title is required and must be"):
            await use_case.execute(
                owner_id=str(uuid4()),
                city_code="TPE",
                title=long_title,
                content="Test content",
            )

        mock_post_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_post_missing_content(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test post creation fails when content is missing"""
        # Act & Assert
        with pytest.raises(ValueError, match="Content is required"):
            await use_case.execute(
                owner_id=str(uuid4()),
                city_code="TPE",
                title="Test Post",
                content="",
            )

        mock_post_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_post_with_custom_expiry(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test post creation with custom expiry date"""
        # Arrange
        owner_id = str(uuid4())
        custom_expiry = datetime.now(timezone.utc) + timedelta(days=7)

        # Mock premium subscription
        mock_subscription = AsyncMock()
        mock_subscription.is_premium.return_value = True
        mock_subscription_repository.get_by_user_id.return_value = mock_subscription

        # Mock post creation
        def create_side_effect(post):
            return post

        mock_post_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            owner_id=owner_id,
            city_code="TPE",
            title="Test Post",
            content="Test content",
            expires_at=custom_expiry,
        )

        # Assert
        assert result is not None
        assert result.expires_at == custom_expiry

    @pytest.mark.asyncio
    async def test_create_post_expiry_in_past(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test post creation fails when expiry is in the past"""
        # Arrange
        past_expiry = datetime.now(timezone.utc) - timedelta(days=1)

        # Mock premium subscription
        mock_subscription = AsyncMock()
        mock_subscription.is_premium.return_value = True
        mock_subscription_repository.get_by_user_id.return_value = mock_subscription

        # Act & Assert
        with pytest.raises(ValueError, match="Expiry date must be in the future"):
            await use_case.execute(
                owner_id=str(uuid4()),
                city_code="TPE",
                title="Test Post",
                content="Test content",
                expires_at=past_expiry,
            )

        mock_post_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_post_with_idol_filters(
        self, use_case, mock_post_repository, mock_subscription_repository
    ):
        """Test post creation with idol and idol_group filters"""
        # Arrange
        owner_id = str(uuid4())
        idol = "IU"
        idol_group = "Solo"

        # Mock premium subscription
        mock_subscription = AsyncMock()
        mock_subscription.is_premium.return_value = True
        mock_subscription_repository.get_by_user_id.return_value = mock_subscription

        # Mock post creation
        def create_side_effect(post):
            return post

        mock_post_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            owner_id=owner_id,
            city_code="TPE",
            title="Test Post",
            content="Test content",
            idol=idol,
            idol_group=idol_group,
        )

        # Assert
        assert result is not None
        assert result.idol == idol
        assert result.idol_group == idol_group
