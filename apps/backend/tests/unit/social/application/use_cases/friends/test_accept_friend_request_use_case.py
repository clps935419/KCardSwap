"""
Unit tests for AcceptFriendRequestUseCase
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.modules.social.application.use_cases.friends.accept_friend_request_use_case import (
    AcceptFriendRequestUseCase,
)
from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus


class TestAcceptFriendRequestUseCase:
    """Test AcceptFriendRequestUseCase"""

    @pytest.fixture
    def mock_friendship_repository(self):
        """Create mock friendship repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_chat_room_repository(self):
        """Create mock chat room repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_friendship_repository, mock_chat_room_repository):
        """Create use case instance"""
        return AcceptFriendRequestUseCase(
            friendship_repository=mock_friendship_repository,
            chat_room_repository=mock_chat_room_repository,
        )

    @pytest.mark.asyncio
    async def test_accept_friend_request_success_creates_chat_room(
        self, use_case, mock_friendship_repository, mock_chat_room_repository
    ):
        """Test successful friend request acceptance creates chat room"""
        # Arrange
        friendship_id = "friendship-123"
        user_id = "user-123"
        friend_id = "user-456"
        accepting_user_id = friend_id

        # Mock pending friendship
        friendship = Friendship(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_id.return_value = friendship

        # Mock update to return accepted friendship
        def update_side_effect(friendship):
            return friendship

        mock_friendship_repository.update.side_effect = update_side_effect

        # Mock no existing chat room
        mock_chat_room_repository.get_by_participants.return_value = None

        # Mock create to return new chat room
        def create_chat_room_side_effect(chat_room):
            return chat_room

        mock_chat_room_repository.create.side_effect = create_chat_room_side_effect

        # Act
        updated_friendship, chat_room = await use_case.execute(
            friendship_id, accepting_user_id
        )

        # Assert
        assert updated_friendship is not None
        assert updated_friendship.status == FriendshipStatus.ACCEPTED
        assert chat_room is not None
        assert set(chat_room.participant_ids) == {user_id, friend_id}

        # Verify repository calls
        mock_friendship_repository.get_by_id.assert_called_once_with(friendship_id)
        mock_friendship_repository.update.assert_called_once()
        mock_chat_room_repository.get_by_participants.assert_called_once_with(
            user_id, friend_id
        )
        mock_chat_room_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_friend_request_success_uses_existing_chat_room(
        self, use_case, mock_friendship_repository, mock_chat_room_repository
    ):
        """Test acceptance uses existing chat room if it exists"""
        # Arrange
        friendship_id = "friendship-123"
        user_id = "user-123"
        friend_id = "user-456"
        accepting_user_id = friend_id

        # Mock pending friendship
        friendship = Friendship(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_id.return_value = friendship

        # Mock update
        def update_side_effect(friendship):
            return friendship

        mock_friendship_repository.update.side_effect = update_side_effect

        # Mock existing chat room
        existing_chat_room = ChatRoom(
            id="room-789",
            participant_ids=[user_id, friend_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_participants.return_value = existing_chat_room

        # Act
        updated_friendship, chat_room = await use_case.execute(
            friendship_id, accepting_user_id
        )

        # Assert
        assert updated_friendship is not None
        assert updated_friendship.status == FriendshipStatus.ACCEPTED
        assert chat_room == existing_chat_room

        # Verify chat room was not created (existing one was used)
        mock_chat_room_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_accept_friend_request_not_found(
        self, use_case, mock_friendship_repository, mock_chat_room_repository
    ):
        """Test error when friend request not found"""
        # Arrange
        friendship_id = "friendship-123"
        accepting_user_id = "user-456"

        # Mock no friendship found
        mock_friendship_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Friend request not found"):
            await use_case.execute(friendship_id, accepting_user_id)

        # Verify no updates or creates
        mock_friendship_repository.update.assert_not_called()
        mock_chat_room_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_accept_friend_request_not_recipient(
        self, use_case, mock_friendship_repository, mock_chat_room_repository
    ):
        """Test only recipient can accept request"""
        # Arrange
        friendship_id = "friendship-123"
        user_id = "user-123"
        friend_id = "user-456"
        accepting_user_id = user_id  # Wrong user (initiator, not recipient)

        # Mock pending friendship
        friendship = Friendship(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_id.return_value = friendship

        # Act & Assert
        with pytest.raises(
            ValueError, match="Only the recipient can accept a friend request"
        ):
            await use_case.execute(friendship_id, accepting_user_id)

        # Verify no updates or creates
        mock_friendship_repository.update.assert_not_called()
        mock_chat_room_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_accept_friend_request_not_pending(
        self, use_case, mock_friendship_repository, mock_chat_room_repository
    ):
        """Test cannot accept non-pending request"""
        # Arrange
        friendship_id = "friendship-123"
        user_id = "user-123"
        friend_id = "user-456"
        accepting_user_id = friend_id

        # Mock already accepted friendship
        friendship = Friendship(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_id.return_value = friendship

        # Act & Assert
        with pytest.raises(ValueError, match="Friend request is not pending"):
            await use_case.execute(friendship_id, accepting_user_id)

        # Verify no updates or creates
        mock_friendship_repository.update.assert_not_called()
        mock_chat_room_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_accept_blocked_friendship(
        self, use_case, mock_friendship_repository, mock_chat_room_repository
    ):
        """Test cannot accept blocked friendship"""
        # Arrange
        friendship_id = "friendship-123"
        user_id = "user-123"
        friend_id = "user-456"
        accepting_user_id = friend_id

        # Mock blocked friendship
        friendship = Friendship(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.BLOCKED,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_id.return_value = friendship

        # Act & Assert
        with pytest.raises(ValueError, match="Friend request is not pending"):
            await use_case.execute(friendship_id, accepting_user_id)

        # Verify no updates or creates
        mock_friendship_repository.update.assert_not_called()
        mock_chat_room_repository.create.assert_not_called()
