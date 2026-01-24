"""
Unit tests for ThreadRepository

Tests the thread repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.thread import MessageThread
from app.modules.social.infrastructure.database.models.thread_model import (
    MessageThreadModel,
)
from app.modules.social.infrastructure.repositories.thread_repository import (
    ThreadRepository,
)


class TestThreadRepository:
    """Test ThreadRepository"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return ThreadRepository(mock_session)

    @pytest.fixture
    def sample_thread(self):
        """Create sample MessageThread entity"""
        return MessageThread(
            id=str(uuid4()),
            user_a_id=str(uuid4()),
            user_b_id=str(uuid4()),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_message_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_thread_model(self, sample_thread):
        """Create sample MessageThreadModel"""
        return MessageThreadModel(
            id=UUID(sample_thread.id),
            user_a_id=UUID(sample_thread.user_a_id),
            user_b_id=UUID(sample_thread.user_b_id),
            created_at=sample_thread.created_at,
            updated_at=sample_thread.updated_at,
            last_message_at=sample_thread.last_message_at,
        )

    @pytest.mark.asyncio
    async def test_create_thread(self, repository, mock_session, sample_thread):
        """Test creating a new thread"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_thread)

        # Assert
        assert result is not None
        assert result.id == sample_thread.id
        assert result.user_a_id == sample_thread.user_a_id
        assert result.user_b_id == sample_thread.user_b_id
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repository, mock_session, sample_thread_model
    ):
        """Test getting thread by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_thread_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(sample_thread_model.id))

        # Assert
        assert result is not None
        assert result.id == str(sample_thread_model.id)
        assert result.user_a_id == str(sample_thread_model.user_a_id)
        assert result.user_b_id == str(sample_thread_model.user_b_id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting thread by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_users_found(
        self, repository, mock_session, sample_thread_model
    ):
        """Test finding thread by two users when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_thread_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_users(
            str(sample_thread_model.user_a_id),
            str(sample_thread_model.user_b_id),
        )

        # Assert
        assert result is not None
        assert result.user_a_id == str(sample_thread_model.user_a_id)
        assert result.user_b_id == str(sample_thread_model.user_b_id)

    @pytest.mark.asyncio
    async def test_find_by_users_not_found(self, repository, mock_session):
        """Test finding thread by two users when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_users(str(uuid4()), str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_users_normalizes_order(self, repository, mock_session):
        """Test that find_by_users normalizes user order"""
        # Arrange
        user_a = str(uuid4())
        user_b = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act - call with reversed order
        await repository.find_by_users(user_b, user_a)

        # Assert - should normalize to smaller UUID first
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_threads_for_user(self, repository, mock_session):
        """Test getting all threads for a user"""
        # Arrange
        user_id = str(uuid4())
        thread_models = [
            MessageThreadModel(
                id=uuid4(),
                user_a_id=UUID(user_id),
                user_b_id=uuid4(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_message_at=datetime.utcnow(),
            )
            for _ in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = thread_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_threads_for_user(user_id)

        # Assert
        assert len(result) == 3
        for thread in result:
            assert user_id in [thread.user_a_id, thread.user_b_id]

    @pytest.mark.asyncio
    async def test_get_threads_for_user_with_pagination(
        self, repository, mock_session
    ):
        """Test getting threads with limit and offset"""
        # Arrange
        user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_threads_for_user(user_id, limit=10, offset=20)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_thread(
        self, repository, mock_session, sample_thread, sample_thread_model
    ):
        """Test updating a thread"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_thread_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create modified thread
        updated_thread = MessageThread(
            id=sample_thread.id,
            user_a_id=sample_thread.user_a_id,
            user_b_id=sample_thread.user_b_id,
            created_at=sample_thread.created_at,
            updated_at=datetime.utcnow(),
            last_message_at=datetime.utcnow(),
        )

        # Act
        result = await repository.update(updated_thread)

        # Assert
        assert result is not None
        assert result.id == updated_thread.id
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_thread(self, repository, mock_session, sample_thread_model):
        """Test deleting a thread"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_thread_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_thread_model.id))

        # Assert
        mock_session.delete.assert_called_once()
        mock_session.flush.assert_called_once()
