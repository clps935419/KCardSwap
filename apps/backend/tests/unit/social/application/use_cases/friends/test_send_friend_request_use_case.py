"""
Unit tests for SendFriendRequestUseCase
"""

from unittest.mock import AsyncMock

import pytest

from app.modules.social.application.use_cases.friends.send_friend_request_use_case import (
    SendFriendRequestUseCase,
)
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus


class TestSendFriendRequestUseCase:
    """Test SendFriendRequestUseCase"""

    @pytest.fixture
    def mock_friendship_repository(self):
        """Create mock friendship repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_friendship_repository):
        """Create use case instance"""
        return SendFriendRequestUseCase(
            friendship_repository=mock_friendship_repository
        )

    @pytest.mark.asyncio
    async def test_send_friend_request_success(
        self, use_case, mock_friendship_repository
    ):
        """Test successful friend request creation"""
        # Arrange
        user_id = "user-123"
        friend_id = "user-456"

        # Mock no existing friendship
        mock_friendship_repository.get_by_users.return_value = None
        mock_friendship_repository.is_blocked.return_value = False

        # Mock create to return a friendship with the expected status
        def create_side_effect(friendship):
            return friendship

        mock_friendship_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(user_id, friend_id)

        # Assert
        assert result is not None
        assert result.user_id == user_id
        assert result.friend_id == friend_id
        assert result.status == FriendshipStatus.PENDING

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            user_id, friend_id
        )
        mock_friendship_repository.is_blocked.assert_called_once_with(user_id, friend_id)
        mock_friendship_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_friend_request_to_self(
        self, use_case, mock_friendship_repository
    ):
        """Test cannot send friend request to self"""
        # Arrange
        user_id = "user-123"

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot send friend request to yourself"):
            await use_case.execute(user_id, user_id)

        # Verify no repository calls were made
        mock_friendship_repository.get_by_users.assert_not_called()
        mock_friendship_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_friend_request_already_friends(
        self, use_case, mock_friendship_repository
    ):
        """Test cannot send request when already friends"""
        # Arrange
        user_id = "user-123"
        friend_id = "user-456"

        # Mock existing accepted friendship
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.ACCEPTED,
            created_at=None,
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Act & Assert
        with pytest.raises(ValueError, match="Users are already friends"):
            await use_case.execute(user_id, friend_id)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            user_id, friend_id
        )
        mock_friendship_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_friend_request_already_pending(
        self, use_case, mock_friendship_repository
    ):
        """Test cannot send request when already pending"""
        # Arrange
        user_id = "user-123"
        friend_id = "user-456"

        # Mock existing pending friendship
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.PENDING,
            created_at=None,
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Act & Assert
        with pytest.raises(ValueError, match="Friend request already pending"):
            await use_case.execute(user_id, friend_id)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            user_id, friend_id
        )
        mock_friendship_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_friend_request_user_blocked(
        self, use_case, mock_friendship_repository
    ):
        """Test cannot send request when user is blocked"""
        # Arrange
        user_id = "user-123"
        friend_id = "user-456"

        # Mock existing blocked relationship
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.BLOCKED,
            created_at=None,
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot send friend request - user is blocked"
        ):
            await use_case.execute(user_id, friend_id)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            user_id, friend_id
        )
        mock_friendship_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_friend_request_blocked_by_other_user(
        self, use_case, mock_friendship_repository
    ):
        """Test cannot send request when blocked by other user"""
        # Arrange
        user_id = "user-123"
        friend_id = "user-456"

        # Mock no existing friendship in one direction
        mock_friendship_repository.get_by_users.return_value = None
        # Mock blocked in reverse direction
        mock_friendship_repository.is_blocked.return_value = True

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot send friend request - you are blocked by this user"
        ):
            await use_case.execute(user_id, friend_id)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            user_id, friend_id
        )
        mock_friendship_repository.is_blocked.assert_called_once_with(user_id, friend_id)
        mock_friendship_repository.create.assert_not_called()
