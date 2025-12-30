"""
Unit tests for BlockUserUseCase
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.modules.social.application.use_cases.friends.block_user_use_case import (
    BlockUserUseCase,
)
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus


class TestBlockUserUseCase:
    """Test BlockUserUseCase"""

    @pytest.fixture
    def mock_friendship_repository(self):
        """Create mock friendship repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_friendship_repository):
        """Create use case instance"""
        return BlockUserUseCase(friendship_repository=mock_friendship_repository)

    @pytest.mark.asyncio
    async def test_block_user_success_new_relationship(
        self, use_case, mock_friendship_repository
    ):
        """Test successfully blocking a user with no existing relationship"""
        # Arrange
        blocker_user_id = "user-123"
        blocked_user_id = "user-456"

        # Mock no existing friendship
        mock_friendship_repository.get_by_users.return_value = None

        # Mock create to return friendship
        def create_side_effect(friendship):
            return friendship

        mock_friendship_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(blocker_user_id, blocked_user_id)

        # Assert
        assert result is not None
        assert result.user_id == blocker_user_id
        assert result.friend_id == blocked_user_id
        assert result.status == FriendshipStatus.BLOCKED

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            blocker_user_id, blocked_user_id
        )
        mock_friendship_repository.create.assert_called_once()
        mock_friendship_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_block_user_success_existing_pending_relationship(
        self, use_case, mock_friendship_repository
    ):
        """Test blocking a user with existing pending friendship"""
        # Arrange
        blocker_user_id = "user-123"
        blocked_user_id = "user-456"

        # Mock existing pending friendship
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=blocker_user_id,
            friend_id=blocked_user_id,
            status=FriendshipStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Mock update to return updated friendship
        def update_side_effect(friendship):
            return friendship

        mock_friendship_repository.update.side_effect = update_side_effect

        # Act
        result = await use_case.execute(blocker_user_id, blocked_user_id)

        # Assert
        assert result is not None
        assert result.status == FriendshipStatus.BLOCKED

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            blocker_user_id, blocked_user_id
        )
        mock_friendship_repository.update.assert_called_once()
        mock_friendship_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_block_user_success_existing_accepted_relationship(
        self, use_case, mock_friendship_repository
    ):
        """Test blocking a user with existing accepted friendship"""
        # Arrange
        blocker_user_id = "user-123"
        blocked_user_id = "user-456"

        # Mock existing accepted friendship
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=blocker_user_id,
            friend_id=blocked_user_id,
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Mock update to return updated friendship
        def update_side_effect(friendship):
            return friendship

        mock_friendship_repository.update.side_effect = update_side_effect

        # Act
        result = await use_case.execute(blocker_user_id, blocked_user_id)

        # Assert
        assert result is not None
        assert result.status == FriendshipStatus.BLOCKED

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            blocker_user_id, blocked_user_id
        )
        mock_friendship_repository.update.assert_called_once()
        mock_friendship_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_block_user_already_blocked(
        self, use_case, mock_friendship_repository
    ):
        """Test blocking a user who is already blocked (idempotent)"""
        # Arrange
        blocker_user_id = "user-123"
        blocked_user_id = "user-456"

        # Mock existing blocked relationship
        existing_friendship = Friendship(
            id="friendship-1",
            user_id=blocker_user_id,
            friend_id=blocked_user_id,
            status=FriendshipStatus.BLOCKED,
            created_at=datetime.utcnow(),
        )
        mock_friendship_repository.get_by_users.return_value = existing_friendship

        # Mock update to return updated friendship
        def update_side_effect(friendship):
            return friendship

        mock_friendship_repository.update.side_effect = update_side_effect

        # Act
        result = await use_case.execute(blocker_user_id, blocked_user_id)

        # Assert
        assert result is not None
        assert result.status == FriendshipStatus.BLOCKED

        # Verify repository calls
        mock_friendship_repository.get_by_users.assert_called_once_with(
            blocker_user_id, blocked_user_id
        )
        mock_friendship_repository.update.assert_called_once()
        mock_friendship_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_block_user_cannot_block_self(
        self, use_case, mock_friendship_repository
    ):
        """Test cannot block yourself"""
        # Arrange
        user_id = "user-123"

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot block yourself"):
            await use_case.execute(user_id, user_id)

        # Verify no repository calls
        mock_friendship_repository.get_by_users.assert_not_called()
        mock_friendship_repository.create.assert_not_called()
        mock_friendship_repository.update.assert_not_called()
