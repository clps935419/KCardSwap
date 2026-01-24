"""
Unit tests for Posts Router

Tests the posts router endpoints with mocked use cases.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.modules.posts.domain.entities.post_enums import PostCategory, PostScope
from app.modules.posts.presentation.routers.posts_router import (
    close_post,
    create_post,
    list_posts,
    toggle_like,
)
from app.modules.posts.presentation.schemas.post_schemas import (
    CreatePostRequest,
)


class TestPostsRouter:
    """Test Posts Router endpoints"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        return AsyncMock()

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_post_id(self):
        """Create sample post ID"""
        return uuid4()

    @pytest.fixture
    def mock_post(self, sample_post_id, sample_user_id):
        """Create mock post entity"""
        post = MagicMock()
        post.id = str(sample_post_id)
        post.owner_id = str(sample_user_id)
        post.scope = PostScope.CITY
        post.city_code = "TPE"
        post.category = PostCategory.TRADE
        post.title = "Looking for Minji photocard"
        post.content = "I have Hanni, looking to trade for Minji"
        post.idol = "Minji"
        post.idol_group = "NewJeans"
        post.status = MagicMock(value="open")
        post.expires_at = datetime.now(timezone.utc)
        post.created_at = datetime.now(timezone.utc)
        post.updated_at = datetime.now(timezone.utc)
        return post

    @pytest.fixture
    def mock_post_with_likes(self, mock_post):
        """Create mock post with like data"""
        pwl = MagicMock()
        pwl.post = mock_post
        pwl.like_count = 5
        pwl.liked_by_me = True
        return pwl

    @pytest.fixture
    def mock_create_use_case(self):
        """Create mock create post use case"""
        return AsyncMock()

    @pytest.fixture
    def mock_list_use_case(self):
        """Create mock list posts use case"""
        return AsyncMock()

    @pytest.fixture
    def mock_close_use_case(self):
        """Create mock close post use case"""
        return AsyncMock()

    @pytest.fixture
    def mock_toggle_like_use_case(self):
        """Create mock toggle like use case"""
        return AsyncMock()

    # Tests for POST /posts
    @pytest.mark.asyncio
    async def test_create_post_success(
        self,
        mock_session,
        sample_user_id,
        mock_post,
        mock_create_use_case,
    ):
        """Test successful post creation"""
        # Arrange
        request = CreatePostRequest(
            scope="city",
            category="trade",
            city_code="TPE",
            title="Looking for Minji photocard",
            content="I have Hanni, looking to trade for Minji",
            idol="Minji",
            idol_group="NewJeans",
        )
        mock_create_use_case.execute.return_value = mock_post

        # Act
        response = await create_post(
            request=request,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_create_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.id == UUID(mock_post.id)
        assert response.data.title == mock_post.title
        assert response.data.scope == "city"
        assert response.data.category == "trade"
        assert response.error is None
        mock_create_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_post_global_scope(
        self,
        mock_session,
        sample_user_id,
        mock_post,
        mock_create_use_case,
    ):
        """Test post creation with global scope"""
        # Arrange
        mock_post.scope = PostScope.GLOBAL
        mock_post.city_code = None
        request = CreatePostRequest(
            scope="global",
            category="trade",
            title="Looking for rare photocards",
            content="Trading multiple cards",
            idol="Minji",
            idol_group="NewJeans",
        )
        mock_create_use_case.execute.return_value = mock_post

        # Act
        response = await create_post(
            request=request,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_create_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.scope == "global"
        assert response.error is None

    @pytest.mark.asyncio
    async def test_create_post_validation_error(
        self,
        mock_session,
        sample_user_id,
        mock_create_use_case,
    ):
        """Test post creation with validation error"""
        # Arrange
        request = CreatePostRequest(
            scope="city",
            category="trade",
            title="Test",
            content="Test content",
        )
        mock_create_use_case.execute.side_effect = ValueError(
            "City code required for city scope"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_post(
                request=request,
                current_user_id=sample_user_id,
                session=mock_session,
                use_case=mock_create_use_case,
            )

        assert exc_info.value.status_code == 422
        assert "City code required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_post_daily_limit_exceeded(
        self,
        mock_session,
        sample_user_id,
        mock_create_use_case,
    ):
        """Test post creation with daily limit exceeded"""
        # Arrange
        request = CreatePostRequest(
            scope="city",
            category="trade",
            city_code="TPE",
            title="Test",
            content="Test content",
        )
        mock_create_use_case.execute.side_effect = ValueError(
            "Daily post limit exceeded"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_post(
                request=request,
                current_user_id=sample_user_id,
                session=mock_session,
                use_case=mock_create_use_case,
            )

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_create_post_with_custom_expiry(
        self,
        mock_session,
        sample_user_id,
        mock_post,
        mock_create_use_case,
    ):
        """Test post creation with custom expiry time"""
        # Arrange
        custom_expiry = datetime.now(timezone.utc)
        request = CreatePostRequest(
            scope="city",
            category="trade",
            city_code="TPE",
            title="Test",
            content="Test content",
            expires_at=custom_expiry,
        )
        mock_create_use_case.execute.return_value = mock_post

        # Act
        response = await create_post(
            request=request,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_create_use_case,
        )

        # Assert
        assert response.data is not None
        mock_create_use_case.execute.assert_called_once()
        call_kwargs = mock_create_use_case.execute.call_args[1]
        assert call_kwargs["expires_at"] == custom_expiry

    # Tests for GET /posts
    @pytest.mark.asyncio
    async def test_list_posts_success(
        self,
        mock_session,
        sample_user_id,
        mock_post_with_likes,
        mock_list_use_case,
    ):
        """Test successful post listing"""
        # Arrange
        mock_list_use_case.execute.return_value = [mock_post_with_likes]

        # Act
        response = await list_posts(
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_list_use_case,
            city_code=None,
            category=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert response.data is not None
        assert len(response.data.posts) == 1
        assert response.data.posts[0].id == UUID(mock_post_with_likes.post.id)
        assert response.data.posts[0].like_count == 5
        assert response.data.posts[0].liked_by_me is True
        assert response.error is None
        mock_list_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_posts_with_city_filter(
        self,
        mock_session,
        sample_user_id,
        mock_post_with_likes,
        mock_list_use_case,
    ):
        """Test post listing with city filter"""
        # Arrange
        mock_list_use_case.execute.return_value = [mock_post_with_likes]

        # Act
        response = await list_posts(
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_list_use_case,
            city_code="TPE",
            category=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert response.data is not None
        mock_list_use_case.execute.assert_called_once_with(
            current_user_id=str(sample_user_id),
            city_code="TPE",
            category=None,
            limit=50,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_posts_with_category_filter(
        self,
        mock_session,
        sample_user_id,
        mock_post_with_likes,
        mock_list_use_case,
    ):
        """Test post listing with category filter"""
        # Arrange
        mock_list_use_case.execute.return_value = [mock_post_with_likes]

        # Act
        response = await list_posts(
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_list_use_case,
            city_code=None,
            category=PostCategory.TRADE,
            limit=50,
            offset=0,
        )

        # Assert
        assert response.data is not None
        mock_list_use_case.execute.assert_called_once_with(
            current_user_id=str(sample_user_id),
            city_code=None,
            category=PostCategory.TRADE,
            limit=50,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_posts_with_pagination(
        self,
        mock_session,
        sample_user_id,
        mock_post_with_likes,
        mock_list_use_case,
    ):
        """Test post listing with pagination"""
        # Arrange
        mock_list_use_case.execute.return_value = [mock_post_with_likes]

        # Act
        response = await list_posts(
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_list_use_case,
            city_code=None,
            category=None,
            limit=20,
            offset=40,
        )

        # Assert
        assert response.data is not None
        mock_list_use_case.execute.assert_called_once_with(
            current_user_id=str(sample_user_id),
            city_code=None,
            category=None,
            limit=20,
            offset=40,
        )

    @pytest.mark.asyncio
    async def test_list_posts_empty_list(
        self,
        mock_session,
        sample_user_id,
        mock_list_use_case,
    ):
        """Test post listing with no posts"""
        # Arrange
        mock_list_use_case.execute.return_value = []

        # Act
        response = await list_posts(
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_list_use_case,
            city_code=None,
            category=None,
            limit=50,
            offset=0,
        )

        # Assert
        assert response.data is not None
        assert len(response.data.posts) == 0
        assert response.data.total == 0
        assert response.error is None

    @pytest.mark.asyncio
    async def test_list_posts_validation_error(
        self,
        mock_session,
        sample_user_id,
        mock_list_use_case,
    ):
        """Test post listing with validation error"""
        # Arrange
        mock_list_use_case.execute.side_effect = ValueError("Invalid city code")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_posts(
                current_user_id=sample_user_id,
                session=mock_session,
                use_case=mock_list_use_case,
                city_code="INVALID",
                category=None,
                limit=50,
                offset=0,
            )

        assert exc_info.value.status_code == 400

    # Tests for POST /posts/{post_id}/close
    @pytest.mark.asyncio
    async def test_close_post_success(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_close_use_case,
    ):
        """Test successful post closing"""
        # Arrange
        mock_close_use_case.execute.return_value = None

        # Act
        result = await close_post(
            post_id=sample_post_id,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_close_use_case,
        )

        # Assert
        assert result is None  # 204 No Content
        mock_close_use_case.execute.assert_called_once_with(
            post_id=str(sample_post_id),
            current_user_id=str(sample_user_id),
        )

    @pytest.mark.asyncio
    async def test_close_post_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_close_use_case,
    ):
        """Test close post when post not found"""
        # Arrange
        mock_close_use_case.execute.side_effect = ValueError("Post not found")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await close_post(
                post_id=sample_post_id,
                current_user_id=sample_user_id,
                session=mock_session,
                use_case=mock_close_use_case,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_close_post_not_owner(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_close_use_case,
    ):
        """Test close post when user is not the owner"""
        # Arrange
        mock_close_use_case.execute.side_effect = ValueError(
            "Only post owner can close the post"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await close_post(
                post_id=sample_post_id,
                current_user_id=sample_user_id,
                session=mock_session,
                use_case=mock_close_use_case,
            )

        assert exc_info.value.status_code == 403
        assert "only post owner" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_close_post_already_closed(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_close_use_case,
    ):
        """Test close post when post is already closed"""
        # Arrange
        mock_close_use_case.execute.side_effect = ValueError("Post is not open")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await close_post(
                post_id=sample_post_id,
                current_user_id=sample_user_id,
                session=mock_session,
                use_case=mock_close_use_case,
            )

        assert exc_info.value.status_code == 422

    # Tests for POST /posts/{post_id}/like
    @pytest.mark.asyncio
    async def test_toggle_like_add_like(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_toggle_like_use_case,
    ):
        """Test adding a like to a post"""
        # Arrange
        mock_result = MagicMock()
        mock_result.liked = True
        mock_result.like_count = 6
        mock_toggle_like_use_case.execute.return_value = mock_result

        # Act
        response = await toggle_like(
            post_id=sample_post_id,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_toggle_like_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.liked is True
        assert response.data.like_count == 6
        assert response.error is None
        mock_toggle_like_use_case.execute.assert_called_once_with(
            post_id=str(sample_post_id),
            user_id=str(sample_user_id),
        )

    @pytest.mark.asyncio
    async def test_toggle_like_remove_like(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_toggle_like_use_case,
    ):
        """Test removing a like from a post"""
        # Arrange
        mock_result = MagicMock()
        mock_result.liked = False
        mock_result.like_count = 4
        mock_toggle_like_use_case.execute.return_value = mock_result

        # Act
        response = await toggle_like(
            post_id=sample_post_id,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_toggle_like_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.liked is False
        assert response.data.like_count == 4
        assert response.error is None

    @pytest.mark.asyncio
    async def test_toggle_like_post_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_toggle_like_use_case,
    ):
        """Test toggle like when post not found"""
        # Arrange
        mock_toggle_like_use_case.execute.side_effect = ValueError("Post not found")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await toggle_like(
                post_id=sample_post_id,
                current_user_id=sample_user_id,
                session=mock_session,
                use_case=mock_toggle_like_use_case,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_toggle_like_idempotent(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_toggle_like_use_case,
    ):
        """Test toggle like is idempotent"""
        # Arrange
        mock_result_like = MagicMock()
        mock_result_like.liked = True
        mock_result_like.like_count = 6

        mock_result_unlike = MagicMock()
        mock_result_unlike.liked = False
        mock_result_unlike.like_count = 5

        mock_toggle_like_use_case.execute.side_effect = [
            mock_result_like,
            mock_result_unlike,
        ]

        # Act
        response1 = await toggle_like(
            post_id=sample_post_id,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_toggle_like_use_case,
        )

        response2 = await toggle_like(
            post_id=sample_post_id,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_toggle_like_use_case,
        )

        # Assert
        assert response1.data.liked is True
        assert response1.data.like_count == 6
        assert response2.data.liked is False
        assert response2.data.like_count == 5

    @pytest.mark.asyncio
    async def test_toggle_like_first_like(
        self,
        mock_session,
        sample_user_id,
        sample_post_id,
        mock_toggle_like_use_case,
    ):
        """Test toggle like when post has no likes"""
        # Arrange
        mock_result = MagicMock()
        mock_result.liked = True
        mock_result.like_count = 1
        mock_toggle_like_use_case.execute.return_value = mock_result

        # Act
        response = await toggle_like(
            post_id=sample_post_id,
            current_user_id=sample_user_id,
            session=mock_session,
            use_case=mock_toggle_like_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.liked is True
        assert response.data.like_count == 1

    @pytest.mark.asyncio
    async def test_toggle_like_multiple_users(
        self,
        mock_session,
        sample_post_id,
        mock_toggle_like_use_case,
    ):
        """Test toggle like from multiple different users"""
        # Arrange
        user1_id = uuid4()
        user2_id = uuid4()

        mock_result1 = MagicMock()
        mock_result1.liked = True
        mock_result1.like_count = 1

        mock_result2 = MagicMock()
        mock_result2.liked = True
        mock_result2.like_count = 2

        mock_toggle_like_use_case.execute.side_effect = [mock_result1, mock_result2]

        # Act
        response1 = await toggle_like(
            post_id=sample_post_id,
            current_user_id=user1_id,
            session=mock_session,
            use_case=mock_toggle_like_use_case,
        )

        response2 = await toggle_like(
            post_id=sample_post_id,
            current_user_id=user2_id,
            session=mock_session,
            use_case=mock_toggle_like_use_case,
        )

        # Assert
        assert response1.data.like_count == 1
        assert response2.data.like_count == 2
