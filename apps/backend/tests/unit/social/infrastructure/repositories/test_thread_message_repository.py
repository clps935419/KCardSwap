"""
Unit tests for ThreadMessageRepository

Tests the thread message repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.thread_message import ThreadMessage
from app.modules.social.infrastructure.database.models.thread_message_model import (
    ThreadMessageModel,
)
from app.modules.social.infrastructure.repositories.thread_message_repository import (
    ThreadMessageRepository,
)


class TestThreadMessageRepository:
    """Test ThreadMessageRepository"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return ThreadMessageRepository(mock_session)

    @pytest.fixture
    def sample_thread_message(self):
        """Create sample ThreadMessage entity"""
        return ThreadMessage(
            id=str(uuid4()),
            thread_id=str(uuid4()),
            sender_id=str(uuid4()),
            content="Hello from thread message!",
            post_id=str(uuid4()),
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_message_model(self, sample_thread_message):
        """Create sample ThreadMessageModel"""
        return ThreadMessageModel(
            id=UUID(sample_thread_message.id),
            thread_id=UUID(sample_thread_message.thread_id),
            sender_id=UUID(sample_thread_message.sender_id),
            content=sample_thread_message.content,
            post_id=UUID(sample_thread_message.post_id) if sample_thread_message.post_id else None,
            created_at=sample_thread_message.created_at,
        )

    @pytest.mark.asyncio
    async def test_create_thread_message(
        self, repository, mock_session, sample_thread_message
    ):
        """Test creating a new thread message"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_thread_message)

        # Assert
        assert result is not None
        assert result.id == sample_thread_message.id
        assert result.thread_id == sample_thread_message.thread_id
        assert result.content == sample_thread_message.content
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repository, mock_session, sample_message_model
    ):
        """Test getting thread message by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_message_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(sample_message_model.id))

        # Assert
        assert result is not None
        assert result.id == str(sample_message_model.id)
        assert result.content == sample_message_model.content

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting thread message by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_messages_by_thread(self, repository, mock_session):
        """Test getting all messages in a thread"""
        # Arrange
        thread_id = str(uuid4())
        message_models = [
            ThreadMessageModel(
                id=uuid4(),
                thread_id=UUID(thread_id),
                sender_id=uuid4(),
                content=f"Message {i}",
                post_id=None,
                created_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = message_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_messages_by_thread(thread_id)

        # Assert
        assert len(result) == 3
        for msg in result:
            assert msg.thread_id == thread_id

    @pytest.mark.asyncio
    async def test_get_messages_by_thread_with_pagination(
        self, repository, mock_session
    ):
        """Test getting messages with limit and offset"""
        # Arrange
        thread_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_messages_by_thread(
            thread_id, limit=10, offset=5
        )

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_thread_message(
        self, repository, mock_session, sample_message_model
    ):
        """Test deleting a thread message"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_message_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_message_model.id))

        # Assert
        mock_session.delete.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_thread_message_count(self, repository, mock_session):
        """Test getting message count in a thread"""
        # Arrange
        thread_id = str(uuid4())
        expected_count = 15

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_thread_message_count(thread_id)

        # Assert
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_create_message_without_post_id(self, repository, mock_session):
        """Test creating message without post_id"""
        # Arrange
        message = ThreadMessage(
            id=str(uuid4()),
            thread_id=str(uuid4()),
            sender_id=str(uuid4()),
            content="Message without post",
            post_id=None,
            created_at=datetime.utcnow(),
        )
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(message)

        # Assert
        assert result is not None
        assert result.post_id is None
        mock_session.add.assert_called_once()
