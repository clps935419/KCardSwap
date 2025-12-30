"""
Unit tests for UnblockUserUseCase
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.modules.social.application.use_cases.friends.unblock_user_use_case import (
    UnblockUserUseCase,
)
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus


class TestUnblockUserUseCase:
    """Test UnblockUserUseCase"""

    @pytest.fixture
    def mock_friendship_repository(self):
        """Create mock friendship repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_friendship_repository):
        """Create use case instance"""
        return UnblockUserUseCase(friendship_repository=mock_friendship_repository)

    @pytest.mark.asyncio
    async def test_unblock_user_success(self, use_case, mock_friendship_repository):
        """Test successfully unblocking a user"""
        # Arrange
        unblocker_user_id = "user-123"
        unblocked_user_id = "user-456"

        # Mock existing blocked relationship where user-123 blocked user-456
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=unblocker_user_id,  # The blocker
            friend_id=unblocked_user_id,  # The blocked user
            status=FriendshipStatus.BLOCKED,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship
        mock_friendship_repository.delete.return_value = None

        # Act
        result = await use_case.execute(unblocker_user_id, unblocked_user_id)

        # Assert
        assert result is None  # Unblock returns None (relationship deleted)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            unblocker_user_id, unblocked_user_id
        )
        mock_friendship_repository.delete.assert_called_once_with("friendship-1")

    @pytest.mark.asyncio
    async def test_unblock_user_no_relationship_exists(
        self, use_case, mock_friendship_repository
    ):
        """Test unblocking when no relationship exists"""
        # Arrange
        unblocker_user_id = "user-123"
        unblocked_user_id = "user-456"

        # Mock no existing friendship
        mock_friendship_repository.get_by_users.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="No relationship exists with this user"):
            await use_case.execute(unblocker_user_id, unblocked_user_id)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            unblocker_user_id, unblocked_user_id
        )
        mock_friendship_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_unblock_user_relationship_not_blocked_pending(
        self, use_case, mock_friendship_repository
    ):
        """Test unblocking when relationship is pending (not blocked)"""
        # Arrange
        unblocker_user_id = "user-123"
        unblocked_user_id = "user-456"

        # Mock existing pending relationship
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=unblocker_user_id,
            friend_id=unblocked_user_id,
            status=FriendshipStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot unblock: relationship status is pending, not blocked"
        ):
            await use_case.execute(unblocker_user_id, unblocked_user_id)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            unblocker_user_id, unblocked_user_id
        )
        mock_friendship_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_unblock_user_relationship_not_blocked_accepted(
        self, use_case, mock_friendship_repository
    ):
        """Test unblocking when relationship is accepted (not blocked)"""
        # Arrange
        unblocker_user_id = "user-123"
        unblocked_user_id = "user-456"

        # Mock existing accepted relationship
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=unblocker_user_id,
            friend_id=unblocked_user_id,
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot unblock: relationship status is accepted, not blocked"
        ):
            await use_case.execute(unblocker_user_id, unblocked_user_id)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            unblocker_user_id, unblocked_user_id
        )
        mock_friendship_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_unblock_user_not_the_blocker(
        self, use_case, mock_friendship_repository
    ):
        """Test unblocking when current user is not the one who blocked"""
        # Arrange
        unblocker_user_id = "user-123"
        unblocked_user_id = "user-456"

        # Mock existing blocked relationship where user-456 blocked user-123
        # (not the other way around)
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=unblocked_user_id,  # user-456 is the blocker
            friend_id=unblocker_user_id,  # user-123 is blocked
            status=FriendshipStatus.BLOCKED,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Act & Assert
        with pytest.raises(ValueError, match="You are not the one who blocked this user"):
            await use_case.execute(unblocker_user_id, unblocked_user_id)

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            unblocker_user_id, unblocked_user_id
        )
        mock_friendship_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_unblock_user_cannot_unblock_self(
        self, use_case, mock_friendship_repository
    ):
        """Test cannot unblock yourself"""
        # Arrange
        user_id = "user-123"

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot unblock yourself"):
            await use_case.execute(user_id, user_id)

        # Verify no repository calls
        mock_friendship_repository.get_by_users.assert_not_called()
        mock_friendship_repository.delete.assert_not_called()
