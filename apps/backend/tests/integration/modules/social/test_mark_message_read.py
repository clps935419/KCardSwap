"""
Unit tests for mark message as read functionality in chat router

Tests the complete flow of marking a message as read including:
- Business rule validation
- Message status updates
- Database persistence
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.entities.message import Message, MessageStatus

client = TestClient(app)


class TestMarkMessageAsRead:
    """Test mark message as read endpoint"""

    @pytest.fixture
    def test_user_ids(self):
        """Generate test user IDs"""
        return {
            "current_user": uuid4(),
            "other_user": uuid4(),
        }

    @pytest.fixture
    def test_chat_room(self, test_user_ids):
        """Generate test chat room"""
        return ChatRoom(
            id=str(uuid4()),
            participant_ids=[
                str(test_user_ids["current_user"]),
                str(test_user_ids["other_user"]),
            ],
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def test_message_sent(self, test_chat_room, test_user_ids):
        """Generate test message in SENT status"""
        return Message(
            id=str(uuid4()),
            room_id=test_chat_room.id,
            sender_id=str(test_user_ids["other_user"]),
            content="Test message",
            status=MessageStatus.SENT,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def test_message_read(self, test_chat_room, test_user_ids):
        """Generate test message already in READ status"""
        return Message(
            id=str(uuid4()),
            room_id=test_chat_room.id,
            sender_id=str(test_user_ids["other_user"]),
            content="Test message",
            status=MessageStatus.READ,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def mock_auth(self, test_user_ids):
        """Mock authentication"""
        with patch(
            "app.modules.social.presentation.routers.chat_router.get_current_user_id",
            return_value=test_user_ids["current_user"],
        ):
            yield test_user_ids["current_user"]

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        with patch(
            "app.modules.social.presentation.routers.chat_router.get_db_session"
        ) as mock:
            session = Mock()
            mock.return_value = session
            yield session

    @pytest.mark.asyncio
    async def test_mark_message_as_read_success(
        self, mock_auth, mock_db_session, test_chat_room, test_message_sent
    ):
        """Test successfully marking a message as read"""
        # Arrange
        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_message, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.update",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_get_room.return_value = test_chat_room
            mock_get_message.return_value = test_message_sent

            # Mock update to return the updated message
            def update_message(msg):
                return msg

            mock_update.side_effect = update_message

            # Act
            response = client.post(
                f"/api/v1/chats/{test_chat_room.id}/messages/{test_message_sent.id}/read"
            )

            # Assert
            assert response.status_code == status.HTTP_204_NO_CONTENT
            mock_update.assert_called_once()
            # Verify the message status was updated
            updated_message = mock_update.call_args[0][0]
            assert updated_message.status == MessageStatus.READ

    @pytest.mark.asyncio
    async def test_mark_already_read_message(
        self, mock_auth, mock_db_session, test_chat_room, test_message_read
    ):
        """Test marking an already read message (should succeed without update)"""
        # Arrange
        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_message, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.update",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_get_room.return_value = test_chat_room
            mock_get_message.return_value = test_message_read

            # Act
            response = client.post(
                f"/api/v1/chats/{test_chat_room.id}/messages/{test_message_read.id}/read"
            )

            # Assert
            assert response.status_code == status.HTTP_204_NO_CONTENT
            # Should not call update for already read messages
            mock_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_mark_own_message_as_read_fails(
        self, mock_auth, mock_db_session, test_chat_room, test_user_ids
    ):
        """Test that user cannot mark their own message as read"""
        # Arrange
        own_message = Message(
            id=str(uuid4()),
            room_id=test_chat_room.id,
            sender_id=str(test_user_ids["current_user"]),  # Same as current user
            content="My own message",
            status=MessageStatus.SENT,
            created_at=datetime.utcnow(),
        )

        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_message:
            mock_get_room.return_value = test_chat_room
            mock_get_message.return_value = own_message

            # Act
            response = client.post(
                f"/api/v1/chats/{test_chat_room.id}/messages/{own_message.id}/read"
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "Cannot mark your own message" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_message_room_not_found(
        self, mock_auth, mock_db_session, test_message_sent
    ):
        """Test marking message when room doesn't exist"""
        # Arrange
        fake_room_id = str(uuid4())

        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room:
            mock_get_room.return_value = None

            # Act
            response = client.post(
                f"/api/v1/chats/{fake_room_id}/messages/{test_message_sent.id}/read"
            )

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Chat room not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_message_not_participant(
        self, mock_auth, mock_db_session, test_user_ids
    ):
        """Test marking message when user is not a participant"""
        # Arrange
        other_room = ChatRoom(
            id=str(uuid4()),
            participant_ids=[str(uuid4()), str(uuid4())],  # Different users
            created_at=datetime.utcnow(),
        )

        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room:
            mock_get_room.return_value = other_room

            # Act
            response = client.post(
                f"/api/v1/chats/{other_room.id}/messages/{uuid4()}/read"
            )

            # Assert
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "Not authorized" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_message_not_found(
        self, mock_auth, mock_db_session, test_chat_room
    ):
        """Test marking non-existent message"""
        # Arrange
        fake_message_id = str(uuid4())

        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_message:
            mock_get_room.return_value = test_chat_room
            mock_get_message.return_value = None

            # Act
            response = client.post(
                f"/api/v1/chats/{test_chat_room.id}/messages/{fake_message_id}/read"
            )

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Message not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_delivered_message_as_read(
        self, mock_auth, mock_db_session, test_chat_room, test_user_ids
    ):
        """Test marking a DELIVERED message as read"""
        # Arrange
        delivered_message = Message(
            id=str(uuid4()),
            room_id=test_chat_room.id,
            sender_id=str(test_user_ids["other_user"]),
            content="Test message",
            status=MessageStatus.DELIVERED,
            created_at=datetime.utcnow(),
        )

        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_message, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.update",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_get_room.return_value = test_chat_room
            mock_get_message.return_value = delivered_message

            def update_message(msg):
                return msg

            mock_update.side_effect = update_message

            # Act
            response = client.post(
                f"/api/v1/chats/{test_chat_room.id}/messages/{delivered_message.id}/read"
            )

            # Assert
            assert response.status_code == status.HTTP_204_NO_CONTENT
            mock_update.assert_called_once()
            updated_message = mock_update.call_args[0][0]
            assert updated_message.status == MessageStatus.READ
