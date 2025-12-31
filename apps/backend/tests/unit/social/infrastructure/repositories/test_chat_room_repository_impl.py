"""
Unit tests for ChatRoomRepositoryImpl

Tests the repository implementation with mocked database session
to ensure correct method implementations and entity conversions.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.infrastructure.database.models.chat_room_model import (
    ChatRoomModel,
)
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
)


class TestChatRoomRepositoryImpl:
    """Test ChatRoomRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return ChatRoomRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_room_id(self):
        """Sample room ID"""
        return str(uuid4())

    @pytest.fixture
    def sample_user_ids(self):
        """Sample user IDs"""
        return {
            "user_a": str(uuid4()),
            "user_b": str(uuid4()),
        }

    @pytest.fixture
    def sample_chat_room(self, sample_room_id, sample_user_ids):
        """Create sample ChatRoom entity"""
        return ChatRoom(
            id=sample_room_id,
            participant_ids=[sample_user_ids["user_a"], sample_user_ids["user_b"]],
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_chat_room_model(self, sample_room_id, sample_user_ids):
        """Create sample ChatRoomModel"""
        model = ChatRoomModel(
            id=UUID(sample_room_id),
            participant_ids=[
                UUID(sample_user_ids["user_a"]),
                UUID(sample_user_ids["user_b"]),
            ],
            created_at=datetime.utcnow(),
        )
        return model

    @pytest.mark.asyncio
    async def test_create_chat_room(
        self, repository, mock_session, sample_chat_room, sample_chat_room_model
    ):
        """Test creating a chat room"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock the refresh to set model attributes
        async def mock_refresh(model):
            model.id = UUID(sample_chat_room.id)
            model.participant_ids = sorted(
                [UUID(pid) for pid in sample_chat_room.participant_ids]
            )
            model.created_at = sample_chat_room.created_at

        mock_session.refresh.side_effect = mock_refresh

        # Act
        result = await repository.create(sample_chat_room)

        # Assert
        assert result is not None
        assert result.id == sample_chat_room.id
        assert set(result.participant_ids) == set(sample_chat_room.participant_ids)
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repository, mock_session, sample_room_id, sample_chat_room_model
    ):
        """Test getting chat room by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_chat_room_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(sample_room_id)

        # Assert
        assert result is not None
        assert result.id == sample_room_id
        assert len(result.participant_ids) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session, sample_room_id):
        """Test getting chat room by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(sample_room_id)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_participants_found(
        self, repository, mock_session, sample_user_ids, sample_chat_room_model
    ):
        """Test getting chat room by participants when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_chat_room_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_participants(
            sample_user_ids["user_a"], sample_user_ids["user_b"]
        )

        # Assert
        assert result is not None
        assert len(result.participant_ids) == 2
        assert sample_user_ids["user_a"] in result.participant_ids
        assert sample_user_ids["user_b"] in result.participant_ids
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_participants_order_independent(
        self, repository, mock_session, sample_user_ids, sample_chat_room_model
    ):
        """Test that get_by_participants works regardless of parameter order"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_chat_room_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act - reverse the order
        result = await repository.get_by_participants(
            sample_user_ids["user_b"], sample_user_ids["user_a"]
        )

        # Assert - should still find the same room
        assert result is not None
        assert len(result.participant_ids) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_rooms_by_user_id_with_results(
        self, repository, mock_session, sample_user_ids
    ):
        """Test getting all rooms for a user when rooms exist"""
        # Arrange
        room1_model = ChatRoomModel(
            id=uuid4(),
            participant_ids=[
                UUID(sample_user_ids["user_a"]),
                UUID(sample_user_ids["user_b"]),
            ],
            created_at=datetime.utcnow(),
        )
        room2_model = ChatRoomModel(
            id=uuid4(),
            participant_ids=[UUID(sample_user_ids["user_a"]), uuid4()],
            created_at=datetime.utcnow(),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [room1_model, room2_model]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_rooms_by_user_id(sample_user_ids["user_a"])

        # Assert
        assert result is not None
        assert len(result) == 2
        # Verify user_a is in all rooms
        for room in result:
            assert sample_user_ids["user_a"] in room.participant_ids
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_rooms_by_user_id_empty(
        self, repository, mock_session, sample_user_ids
    ):
        """Test getting all rooms for a user when no rooms exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_rooms_by_user_id(sample_user_ids["user_a"])

        # Assert
        assert result is not None
        assert len(result) == 0
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_existing_room(
        self, repository, mock_session, sample_room_id, sample_chat_room_model
    ):
        """Test deleting an existing chat room"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_chat_room_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(sample_room_id)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.delete.assert_called_once_with(sample_chat_room_model)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_non_existing_room(
        self, repository, mock_session, sample_room_id
    ):
        """Test deleting a non-existing chat room"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()

        # Act
        await repository.delete(sample_room_id)

        # Assert
        mock_session.execute.assert_called_once()
        # Delete should not be called for non-existing room
        mock_session.delete.assert_not_called()

    def test_to_entity_conversion(self, sample_chat_room_model):
        """Test conversion from model to entity"""
        # Act
        entity = ChatRoomRepositoryImpl._to_entity(sample_chat_room_model)

        # Assert
        assert entity is not None
        assert entity.id == str(sample_chat_room_model.id)
        assert len(entity.participant_ids) == 2
        # All participant IDs should be strings
        for pid in entity.participant_ids:
            assert isinstance(pid, str)
