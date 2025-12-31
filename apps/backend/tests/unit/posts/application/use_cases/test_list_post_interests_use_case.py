"""
Unit tests for ListPostInterestsUseCase (T1303)
Tests business logic for listing post interests
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.posts.application.use_cases.list_post_interests_use_case import (
    ListPostInterestsUseCase,
)
from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.entities.post_interest import (
    PostInterest,
    PostInterestStatus,
)


class TestListPostInterestsUseCase:
    """Unit tests for ListPostInterestsUseCase"""

    @pytest.fixture
    def mock_post_repository(self):
        """Mock post repository"""
        return Mock()

    @pytest.fixture
    def mock_post_interest_repository(self):
        """Mock post interest repository"""
        return Mock()

    @pytest.fixture
    def use_case(self, mock_post_repository, mock_post_interest_repository):
        """Create use case instance with mocked dependencies"""
        return ListPostInterestsUseCase(
            post_repository=mock_post_repository,
            post_interest_repository=mock_post_interest_repository,
        )

    @pytest.fixture
    def test_post(self):
        """Create test post"""
        post_id = uuid4()
        owner_id = uuid4()
        return Post(
            id=str(post_id),
            owner_id=str(owner_id),
            city_code="TPE",
            title="Test Post",
            content="Test Content",
            status=PostStatus.OPEN,
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def test_interests(self, test_post):
        """Create test interests"""
        return [
            PostInterest(
                id=str(uuid4()),
                post_id=test_post.id,
                user_id=str(uuid4()),
                status=PostInterestStatus.PENDING,
                created_at=datetime.now(timezone.utc),
            ),
            PostInterest(
                id=str(uuid4()),
                post_id=test_post.id,
                user_id=str(uuid4()),
                status=PostInterestStatus.ACCEPTED,
                created_at=datetime.now(timezone.utc),
            ),
            PostInterest(
                id=str(uuid4()),
                post_id=test_post.id,
                user_id=str(uuid4()),
                status=PostInterestStatus.REJECTED,
                created_at=datetime.now(timezone.utc),
            ),
        ]

    @pytest.mark.asyncio
    async def test_list_interests_success(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        test_post,
        test_interests,
    ):
        """Test successfully listing interests as post owner"""
        # Setup
        mock_post_repository.get_by_id = AsyncMock(return_value=test_post)
        mock_post_interest_repository.list_by_post_id = AsyncMock(
            return_value=test_interests
        )

        # Execute
        interests, total = await use_case.execute(
            post_id=test_post.id,
            current_user_id=test_post.owner_id,
            status=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert len(interests) == 3
        assert total == 3
        assert interests == test_interests
        mock_post_repository.get_by_id.assert_called_once_with(test_post.id)
        mock_post_interest_repository.list_by_post_id.assert_called_once_with(
            post_id=test_post.id,
            status=None,
            limit=50,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_interests_with_status_filter(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        test_post,
        test_interests,
    ):
        """Test listing interests with status filter"""
        # Setup
        pending_interests = [i for i in test_interests if i.status == PostInterestStatus.PENDING]
        mock_post_repository.get_by_id = AsyncMock(return_value=test_post)
        mock_post_interest_repository.list_by_post_id = AsyncMock(
            return_value=pending_interests
        )

        # Execute
        interests, total = await use_case.execute(
            post_id=test_post.id,
            current_user_id=test_post.owner_id,
            status=PostInterestStatus.PENDING,
            limit=50,
            offset=0,
        )

        # Assert
        assert len(interests) == 1
        assert total == 1
        assert all(i.status == PostInterestStatus.PENDING for i in interests)
        mock_post_interest_repository.list_by_post_id.assert_called_once_with(
            post_id=test_post.id,
            status=PostInterestStatus.PENDING,
            limit=50,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_interests_with_pagination(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        test_post,
        test_interests,
    ):
        """Test listing interests with pagination"""
        # Setup
        paginated_interests = test_interests[:2]
        mock_post_repository.get_by_id = AsyncMock(return_value=test_post)
        mock_post_interest_repository.list_by_post_id = AsyncMock(
            return_value=paginated_interests
        )

        # Execute
        interests, total = await use_case.execute(
            post_id=test_post.id,
            current_user_id=test_post.owner_id,
            status=None,
            limit=2,
            offset=0,
        )

        # Assert
        assert len(interests) == 2
        assert total == 2
        mock_post_interest_repository.list_by_post_id.assert_called_once_with(
            post_id=test_post.id,
            status=None,
            limit=2,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_interests_post_not_found(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
    ):
        """Test listing interests for non-existent post"""
        # Setup
        mock_post_repository.get_by_id = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(ValueError, match="Post not found"):
            await use_case.execute(
                post_id=str(uuid4()),
                current_user_id=str(uuid4()),
                status=None,
                limit=50,
                offset=0,
            )

        mock_post_interest_repository.list_by_post_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_interests_not_owner(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        test_post,
    ):
        """Test listing interests by non-owner user"""
        # Setup
        mock_post_repository.get_by_id = AsyncMock(return_value=test_post)
        different_user_id = str(uuid4())

        # Execute & Assert
        with pytest.raises(ValueError, match="Only post owner can view interests"):
            await use_case.execute(
                post_id=test_post.id,
                current_user_id=different_user_id,
                status=None,
                limit=50,
                offset=0,
            )

        mock_post_interest_repository.list_by_post_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_interests_empty_result(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        test_post,
    ):
        """Test listing interests when no interests exist"""
        # Setup
        mock_post_repository.get_by_id = AsyncMock(return_value=test_post)
        mock_post_interest_repository.list_by_post_id = AsyncMock(return_value=[])

        # Execute
        interests, total = await use_case.execute(
            post_id=test_post.id,
            current_user_id=test_post.owner_id,
            status=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert len(interests) == 0
        assert total == 0
        assert interests == []
