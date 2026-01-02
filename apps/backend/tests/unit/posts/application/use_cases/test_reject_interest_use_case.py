"""
Unit tests for RejectInterestUseCase

Tests the reject interest use case implementation with mocked repositories.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.posts.application.use_cases.reject_interest_use_case import (
    RejectInterestUseCase,
)
from app.modules.posts.domain.entities.post import Post
from app.modules.posts.domain.entities.post_interest import PostInterest


class TestRejectInterestUseCase:
    """Test RejectInterestUseCase"""

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
        return RejectInterestUseCase(
            post_repository=mock_post_repository,
            post_interest_repository=mock_post_interest_repository,
        )

    @pytest.fixture
    def sample_post(self):
        """Create sample post"""
        return Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            city_code="TPE",
            title="Test Post",
            content="Test content",
            status="active",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_interest(self, sample_post):
        """Create sample pending interest"""
        return PostInterest(
            id=str(uuid4()),
            post_id=sample_post.id,
            user_id=str(uuid4()),
            message="Interested!",
            status="pending",
            created_at=datetime.now(timezone.utc),
        )

    @pytest.mark.asyncio
    async def test_reject_interest_success(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_post,
        sample_interest,
    ):
        """Test successful interest rejection"""
        # Arrange
        mock_post_repository.get_by_id.return_value = sample_post
        mock_post_interest_repository.get_by_id.return_value = sample_interest

        # Act
        await use_case.execute(
            post_id=sample_post.id,
            interest_id=sample_interest.id,
            current_user_id=sample_post.owner_id,
        )

        # Assert
        mock_post_repository.get_by_id.assert_called_once_with(sample_post.id)
        mock_post_interest_repository.get_by_id.assert_called_once_with(
            sample_interest.id
        )
        mock_post_interest_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_interest_post_not_found(
        self, use_case, mock_post_repository
    ):
        """Test rejecting interest for non-existent post"""
        # Arrange
        mock_post_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Post not found"):
            await use_case.execute(
                post_id=str(uuid4()),
                interest_id=str(uuid4()),
                current_user_id=str(uuid4()),
            )

    @pytest.mark.asyncio
    async def test_reject_interest_not_post_owner(
        self,
        use_case,
        mock_post_repository,
        sample_post,
    ):
        """Test that only post owner can reject interest"""
        # Arrange
        mock_post_repository.get_by_id.return_value = sample_post

        # Act & Assert
        with pytest.raises(ValueError, match="Only post owner can reject interests"):
            await use_case.execute(
                post_id=sample_post.id,
                interest_id=str(uuid4()),
                current_user_id=str(uuid4()),  # Different from owner
            )

    @pytest.mark.asyncio
    async def test_reject_interest_not_found(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_post,
    ):
        """Test rejecting non-existent interest"""
        # Arrange
        mock_post_repository.get_by_id.return_value = sample_post
        mock_post_interest_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Interest not found"):
            await use_case.execute(
                post_id=sample_post.id,
                interest_id=str(uuid4()),
                current_user_id=sample_post.owner_id,
            )

    @pytest.mark.asyncio
    async def test_reject_interest_wrong_post(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_post,
        sample_interest,
    ):
        """Test rejecting interest that doesn't belong to the post"""
        # Arrange
        sample_interest.post_id = str(uuid4())  # Different post
        mock_post_repository.get_by_id.return_value = sample_post
        mock_post_interest_repository.get_by_id.return_value = sample_interest

        # Act & Assert
        with pytest.raises(ValueError, match="Interest does not belong to this post"):
            await use_case.execute(
                post_id=sample_post.id,
                interest_id=sample_interest.id,
                current_user_id=sample_post.owner_id,
            )

    @pytest.mark.asyncio
    async def test_reject_interest_already_rejected(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_post,
        sample_interest,
    ):
        """Test rejecting an already rejected interest"""
        # Arrange
        sample_interest.status = "rejected"
        mock_post_repository.get_by_id.return_value = sample_post
        mock_post_interest_repository.get_by_id.return_value = sample_interest

        # Act & Assert
        with pytest.raises(ValueError, match="Interest is already"):
            await use_case.execute(
                post_id=sample_post.id,
                interest_id=sample_interest.id,
                current_user_id=sample_post.owner_id,
            )

    @pytest.mark.asyncio
    async def test_reject_interest_already_accepted(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_post,
        sample_interest,
    ):
        """Test rejecting an already accepted interest"""
        # Arrange
        sample_interest.status = "accepted"
        mock_post_repository.get_by_id.return_value = sample_post
        mock_post_interest_repository.get_by_id.return_value = sample_interest

        # Act & Assert
        with pytest.raises(ValueError, match="Interest is already"):
            await use_case.execute(
                post_id=sample_post.id,
                interest_id=sample_interest.id,
                current_user_id=sample_post.owner_id,
            )
