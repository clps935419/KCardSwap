"""
Unit tests for FriendshipRepositoryImpl

Tests the friendship repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.infrastructure.database.models.friendship_model import (
    FriendshipModel,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)


class TestFriendshipRepositoryImpl:
    """Test FriendshipRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return FriendshipRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_friendship(self):
        """Create sample Friendship entity"""
        return Friendship(
            id=str(uuid4()),
            user_id=str(uuid4()),
            friend_id=str(uuid4()),
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_friendship_model(self, sample_friendship):
        """Create sample FriendshipModel"""
        return FriendshipModel(
            id=UUID(sample_friendship.id),
            user_id=UUID(sample_friendship.user_id),
            friend_id=UUID(sample_friendship.friend_id),
            status=sample_friendship.status.value,
            created_at=sample_friendship.created_at,
        )

    @pytest.mark.asyncio
    async def test_create_friendship(self, repository, mock_session, sample_friendship):
        """Test creating a friendship"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_friendship)

        # Assert
        assert result is not None
        assert result.id == sample_friendship.id
        assert result.status == sample_friendship.status
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repository, mock_session, sample_friendship_model
    ):
        """Test getting friendship by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_friendship_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(sample_friendship_model.id))

        # Assert
        assert result is not None
        assert result.id == str(sample_friendship_model.id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting friendship by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_users_found(
        self, repository, mock_session, sample_friendship_model
    ):
        """Test getting friendship by two users"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_friendship_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_users(
            str(sample_friendship_model.user_id),
            str(sample_friendship_model.friend_id),
        )

        # Assert
        assert result is not None
        assert result.user_id == str(sample_friendship_model.user_id)
        assert result.friend_id == str(sample_friendship_model.friend_id)

    @pytest.mark.asyncio
    async def test_get_by_users_bidirectional(
        self, repository, mock_session, sample_friendship_model
    ):
        """Test that get_by_users works in both directions"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_friendship_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act - reverse the order
        result = await repository.get_by_users(
            str(sample_friendship_model.friend_id),
            str(sample_friendship_model.user_id),
        )

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_friends_by_user_id(self, repository, mock_session):
        """Test getting all friends for a user"""
        # Arrange
        user_id = str(uuid4())
        friendship_models = [
            FriendshipModel(
                id=uuid4(),
                user_id=UUID(user_id),
                friend_id=uuid4(),
                status=FriendshipStatus.ACCEPTED.value,
                created_at=datetime.utcnow(),
            )
            for _ in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = friendship_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_friends_by_user_id(user_id)

        # Assert
        assert len(result) == 3
        for friendship in result:
            assert friendship.user_id == user_id or friendship.friend_id == user_id

    @pytest.mark.asyncio
    async def test_get_friends_by_user_id_with_status_filter(
        self, repository, mock_session
    ):
        """Test getting friends filtered by status"""
        # Arrange
        user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_friends_by_user_id(
            user_id, status=FriendshipStatus.PENDING
        )

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_friendship(
        self, repository, mock_session, sample_friendship, sample_friendship_model
    ):
        """Test updating a friendship"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_friendship_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Modify the friendship
        sample_friendship.status = FriendshipStatus.BLOCKED

        # Act
        result = await repository.update(sample_friendship)

        # Assert
        assert result is not None
        assert result.id == sample_friendship.id

    @pytest.mark.asyncio
    async def test_delete_friendship(
        self, repository, mock_session, sample_friendship_model
    ):
        """Test deleting a friendship"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_friendship_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_friendship_model.id))

        # Assert
        mock_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_blocked_true(self, repository, mock_session):
        """Test checking if user is blocked returns True"""
        # Arrange
        user_id = str(uuid4())
        blocker_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # Found a blocking record
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.is_blocked(user_id, blocker_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_is_blocked_false(self, repository, mock_session):
        """Test checking if user is blocked returns False"""
        # Arrange
        user_id = str(uuid4())
        blocker_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No blocking record
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.is_blocked(user_id, blocker_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_are_friends_true(self, repository, mock_session):
        """Test checking if users are friends returns True"""
        # Arrange
        user_id = str(uuid4())
        friend_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # Found an accepted friendship
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.are_friends(user_id, friend_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_are_friends_false(self, repository, mock_session):
        """Test checking if users are friends returns False"""
        # Arrange
        user_id = str(uuid4())
        friend_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No accepted friendship
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.are_friends(user_id, friend_id)

        # Assert
        assert result is False
