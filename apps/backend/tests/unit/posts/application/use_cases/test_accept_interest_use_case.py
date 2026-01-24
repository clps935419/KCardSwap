"""
Unit tests for AcceptInterestUseCase

Tests the accept interest use case implementation with mocked repositories.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.posts.application.use_cases.accept_interest_use_case import (
    AcceptInterestUseCase,
)
from app.modules.posts.domain.entities.post import Post
from app.modules.posts.domain.entities.post_enums import PostCategory, PostScope
from app.modules.posts.domain.entities.post_interest import PostInterest
from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus


class TestAcceptInterestUseCase:
    """Test AcceptInterestUseCase"""

    @pytest.fixture
    def mock_post_repository(self):
        """Create mock post repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_post_interest_repository(self):
        """Create mock post interest repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_friendship_repository(self):
        """Create mock friendship repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_chat_room_repository(self):
        """Create mock chat room repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(
        self,
        mock_post_repository,
        mock_post_interest_repository,
        mock_friendship_repository,
        mock_chat_room_repository,
    ):
        """Create use case instance"""
        return AcceptInterestUseCase(
            post_repository=mock_post_repository,
            post_interest_repository=mock_post_interest_repository,
            friendship_repository=mock_friendship_repository,
            chat_room_repository=mock_chat_room_repository,
        )

    @pytest.fixture
    def sample_post(self):
        """Create sample post"""
        return Post(
            id=str(uuid4()),
            owner_id=str(uuid4()),
            title="Test Post",
            content="Test content",
            status="active",
            scope=PostScope.CITY,
            category=PostCategory.TRADE,
            expires_at=datetime.now(timezone.utc),
            city_code="TPE",
            created_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_interest(self, sample_post):
        """Create sample pending interest"""
        return PostInterest(
            id=str(uuid4()),
            post_id=sample_post.id,
            user_id=str(uuid4()),
            status="pending",
            created_at=datetime.now(timezone.utc),
        )

    @pytest.mark.asyncio
    async def test_accept_interest_creates_friendship_and_chat_room(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        mock_friendship_repository,
        mock_chat_room_repository,
        sample_post,
        sample_interest,
    ):
        """Test successful interest acceptance with friendship and chat room creation"""
        # Arrange
        from uuid import UUID

        from app.shared.domain.contracts.i_chat_room_service import ChatRoomDTO

        mock_post_repository.get_by_id.return_value = sample_post
        mock_post_interest_repository.get_by_id.return_value = sample_interest

        # Service returns None for no existing friendship
        mock_friendship_repository.get_friendship.return_value = None

        # Service creates friendship
        from app.shared.domain.contracts.i_friendship_service import (
            FriendshipDTO,
            FriendshipStatusDTO,
        )
        new_friendship = FriendshipDTO(
            id=UUID(str(uuid4())),
            user_id=UUID(sample_post.owner_id),
            friend_id=UUID(sample_interest.user_id),
            status=FriendshipStatusDTO.ACCEPTED,
            created_at=datetime.now(timezone.utc),
        )
        mock_friendship_repository.create_friendship.return_value = new_friendship

        # Service creates/returns chat room
        new_chat_room_dto = ChatRoomDTO(
            id=UUID(str(uuid4())),
            participant1_id=UUID(sample_post.owner_id),
            participant2_id=UUID(sample_interest.user_id),
        )
        mock_chat_room_repository.get_or_create_chat_room.return_value = new_chat_room_dto

        # Act
        result = await use_case.execute(
            post_id=sample_post.id,
            interest_id=sample_interest.id,
            current_user_id=sample_post.owner_id,
        )

        # Assert
        assert result is not None
        assert result.interest_id == sample_interest.id
        assert result.friendship_created is True
        assert result.chat_room_id == str(new_chat_room_dto.id)
        mock_post_interest_repository.update.assert_called_once()
        mock_friendship_repository.create_friendship.assert_called_once()
        mock_chat_room_repository.get_or_create_chat_room.assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_interest_reuses_existing_chat_room(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        mock_friendship_repository,
        mock_chat_room_repository,
        sample_post,
        sample_interest,
    ):
        """Test that existing chat room is reused"""
        # Arrange
        from uuid import UUID

        from app.shared.domain.contracts.i_chat_room_service import ChatRoomDTO
        from app.shared.domain.contracts.i_friendship_service import (
            FriendshipDTO,
            FriendshipStatusDTO,
        )

        mock_post_repository.get_by_id.return_value = sample_post
        mock_post_interest_repository.get_by_id.return_value = sample_interest
        mock_friendship_repository.get_friendship.return_value = None

        # Service creates friendship
        new_friendship = FriendshipDTO(
            id=UUID(str(uuid4())),
            user_id=UUID(sample_post.owner_id),
            friend_id=UUID(sample_interest.user_id),
            status=FriendshipStatusDTO.ACCEPTED,
            created_at=datetime.now(timezone.utc),
        )
        mock_friendship_repository.create_friendship.return_value = new_friendship

        # Service returns existing chat room
        existing_chat_room_id = uuid4()
        existing_chat_room_dto = ChatRoomDTO(
            id=existing_chat_room_id,
            participant1_id=UUID(sample_post.owner_id),
            participant2_id=UUID(sample_interest.user_id),
        )
        mock_chat_room_repository.get_or_create_chat_room.return_value = (
            existing_chat_room_dto
        )

        # Act
        result = await use_case.execute(
            post_id=sample_post.id,
            interest_id=sample_interest.id,
            current_user_id=sample_post.owner_id,
        )

        # Assert
        assert result.chat_room_id == str(existing_chat_room_id)
        mock_chat_room_repository.get_or_create_chat_room.assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_interest_with_existing_friendship(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        mock_friendship_repository,
        mock_chat_room_repository,
        sample_post,
        sample_interest,
    ):
        """Test accepting interest when users are already friends"""
        # Arrange
        mock_post_repository.get_by_id.return_value = sample_post
        mock_post_interest_repository.get_by_id.return_value = sample_interest

        existing_friendship = Friendship(
            id=str(uuid4()),
            user_id=sample_post.owner_id,
            friend_id=sample_interest.user_id,
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.now(timezone.utc),
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        existing_chat_room = ChatRoom(
            id=str(uuid4()),
            participant_ids=[sample_post.owner_id, sample_interest.user_id],
            created_at=datetime.now(timezone.utc),
        )
        mock_chat_room_repository.get_by_participants.return_value = existing_chat_room

        # Act
        result = await use_case.execute(
            post_id=sample_post.id,
            interest_id=sample_interest.id,
            current_user_id=sample_post.owner_id,
        )

        # Assert
        assert result.friendship_created is False
        mock_friendship_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_accept_interest_post_not_found(
        self, use_case, mock_post_repository
    ):
        """Test accepting interest for non-existent post"""
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
    async def test_accept_interest_not_post_owner(
        self,
        use_case,
        mock_post_repository,
        sample_post,
    ):
        """Test that only post owner can accept interest"""
        # Arrange
        mock_post_repository.get_by_id.return_value = sample_post

        # Act & Assert
        with pytest.raises(ValueError, match="Only post owner can accept interests"):
            await use_case.execute(
                post_id=sample_post.id,
                interest_id=str(uuid4()),
                current_user_id=str(uuid4()),  # Different from owner
            )

    @pytest.mark.asyncio
    async def test_accept_interest_not_found(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_post,
    ):
        """Test accepting non-existent interest"""
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
    async def test_accept_interest_wrong_post(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_post,
        sample_interest,
    ):
        """Test accepting interest that doesn't belong to the post"""
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
    async def test_accept_interest_already_accepted(
        self,
        use_case,
        mock_post_repository,
        mock_post_interest_repository,
        sample_post,
        sample_interest,
    ):
        """Test accepting an already accepted interest"""
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
