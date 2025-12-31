"""
Unit tests for MessageRepositoryImpl

Tests the message repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.message import Message, MessageStatus
from app.modules.social.infrastructure.database.models.message_model import (
    MessageModel,
)
from app.modules.social.infrastructure.repositories.message_repository_impl import (
    MessageRepositoryImpl,
)


class TestMessageRepositoryImpl:
    """Test MessageRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return MessageRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_message(self):
        """Create sample Message entity"""
        return Message(
            id=str(uuid4()),
            room_id=str(uuid4()),
            sender_id=str(uuid4()),
            content="Test message",
            status=MessageStatus.SENT,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_message_model(self, sample_message):
        """Create sample MessageModel"""
        return MessageModel(
            id=UUID(sample_message.id),
            room_id=UUID(sample_message.room_id),
            sender_id=UUID(sample_message.sender_id),
            content=sample_message.content,
            status=sample_message.status.value,
            created_at=sample_message.created_at,
        )

    @pytest.mark.asyncio
    async def test_create_message(self, repository, mock_session, sample_message):
        """Test creating a message"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_message)

        # Assert
        assert result is not None
        assert result.id == sample_message.id
        assert result.content == sample_message.content
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repository, mock_session, sample_message_model
    ):
        """Test getting message by ID when it exists"""
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
        """Test getting message by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_messages_by_room_id(self, repository, mock_session):
        """Test getting messages by room ID"""
        # Arrange
        room_id = str(uuid4())
        message_models = [
            MessageModel(
                id=uuid4(),
                room_id=UUID(room_id),
                sender_id=uuid4(),
                content=f"Message {i}",
                status="sent",
                created_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = message_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_messages_by_room_id(room_id)

        # Assert
        assert len(result) == 3
        for msg in result:
            assert msg.room_id == room_id

    @pytest.mark.asyncio
    async def test_get_messages_by_room_id_with_cursor(
        self, repository, mock_session
    ):
        """Test getting messages with after_message_id cursor"""
        # Arrange
        room_id = str(uuid4())
        after_message_id = str(uuid4())
        message_models = []

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = message_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_messages_by_room_id(
            room_id, after_message_id=after_message_id, limit=10
        )

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_message(
        self, repository, mock_session, sample_message, sample_message_model
    ):
        """Test updating a message"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_message_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Modify the message
        sample_message.status = MessageStatus.READ

        # Act
        result = await repository.update(sample_message)

        # Assert
        assert result is not None
        assert result.id == sample_message.id

    @pytest.mark.asyncio
    async def test_delete_message(self, repository, mock_session, sample_message_model):
        """Test deleting a message"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_message_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_message_model.id))

        # Assert
        mock_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_unread_count_by_room_id(self, repository, mock_session):
        """Test getting unread message count"""
        # Arrange
        room_id = str(uuid4())
        user_id = str(uuid4())
        expected_count = 5

        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_unread_count_by_room_id(room_id, user_id)

        # Assert
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_mark_messages_as_read(self, repository, mock_session):
        """Test marking messages as read"""
        # Arrange
        room_id = str(uuid4())
        user_id = str(uuid4())
        expected_count = 3

        mock_result = MagicMock()
        mock_result.rowcount = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.mark_messages_as_read(room_id, user_id)

        # Assert
        assert result == expected_count
