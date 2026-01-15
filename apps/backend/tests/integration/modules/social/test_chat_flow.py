"""
Integration tests for Chat Router

Tests the complete chat router flow with mocked dependencies to ensure:
1. Router correctly calls repository methods
2. Entity attributes are accessed properly
3. Response schemas are correctly populated
4. Error handling works as expected
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
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestChatRouterIntegration:
    """Integration tests for chat router"""

    @pytest.fixture
    def test_user_ids(self):
        """Generate test user IDs"""
        return {
            "current_user": uuid4(),
            "other_user": uuid4(),
        }

    @pytest.fixture
    def test_chat_rooms(self, test_user_ids):
        """Generate test chat rooms"""
        return [
            ChatRoom(
                id=str(uuid4()),
                participant_ids=[
                    str(test_user_ids["current_user"]),
                    str(test_user_ids["other_user"]),
                ],
                created_at=datetime.utcnow(),
            ),
            ChatRoom(
                id=str(uuid4()),
                participant_ids=[str(test_user_ids["current_user"]), str(uuid4())],
                created_at=datetime.utcnow(),
            ),
        ]

    @pytest.fixture
    def mock_auth(self, test_user_ids):
        """Mock authentication using dependency override"""
        async def override_get_current_user_id() -> UUID:
            return test_user_ids["current_user"]
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield test_user_ids["current_user"]
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session using dependency override"""
        mock_session = Mock()
        
        async def override_get_db_session():
            return mock_session
        
        app.dependency_overrides[get_db_session] = override_get_db_session
        yield mock_session
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_chat_rooms_success(
        self, mock_auth, mock_db_session, test_user_ids, test_chat_rooms
    ):
        """Test successfully getting chat rooms"""
        # Arrange
        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_rooms_by_user_id",
            new_callable=AsyncMock,
        ) as mock_get_rooms:
            mock_get_rooms.return_value = test_chat_rooms

            # Act
            response = client.get("/api/v1/chats")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert "rooms" in data
            assert len(data["rooms"]) == 2

            # Verify each room has correct structure
            for room_data in data["rooms"]:
                assert "id" in room_data
                assert "participants" in room_data
                assert "created_at" in room_data
                assert isinstance(room_data["participants"], list)
                assert len(room_data["participants"]) == 2

                # Verify participants structure
                for participant in room_data["participants"]:
                    assert "user_id" in participant

            # Verify the repository method was called correctly
            mock_get_rooms.assert_called_once_with(str(test_user_ids["current_user"]))

    @pytest.mark.asyncio
    async def test_get_chat_rooms_empty(self, mock_auth, mock_db_session):
        """Test getting chat rooms when user has no rooms"""
        # Arrange
        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_rooms_by_user_id",
            new_callable=AsyncMock,
        ) as mock_get_rooms:
            mock_get_rooms.return_value = []

            # Act
            response = client.get("/api/v1/chats")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert "rooms" in data
            assert len(data["rooms"]) == 0

    @pytest.mark.asyncio
    async def test_get_chat_rooms_participant_ids_iteration(
        self, mock_auth, mock_db_session, test_user_ids
    ):
        """Test that participant_ids are correctly iterated (not user_a_id/user_b_id)"""
        # Arrange
        room_id = str(uuid4())
        user_a = str(test_user_ids["current_user"])
        user_b = str(uuid4())

        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[user_a, user_b],
            created_at=datetime.utcnow(),
        )

        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_rooms_by_user_id",
            new_callable=AsyncMock,
        ) as mock_get_rooms:
            mock_get_rooms.return_value = [chat_room]

            # Act
            response = client.get("/api/v1/chats")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert "rooms" in data
            assert len(data["rooms"]) == 1

            # Verify participants are extracted from participant_ids
            room_data = data["rooms"][0]
            participant_ids = [p["user_id"] for p in room_data["participants"]]
            assert user_a in participant_ids
            assert user_b in participant_ids

    @pytest.mark.asyncio
    async def test_get_chat_rooms_error_handling(self, mock_auth, mock_db_session):
        """Test error handling when repository raises exception"""
        # Arrange
        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_rooms_by_user_id",
            new_callable=AsyncMock,
        ) as mock_get_rooms:
            mock_get_rooms.side_effect = Exception("Database error")

            # Act
            response = client.get("/api/v1/chats")

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_get_messages_success(
        self, mock_auth, mock_db_session, test_user_ids, test_chat_rooms
    ):
        """Test successfully getting messages from a chat room"""
        # Arrange
        room = test_chat_rooms[0]
        messages = [
            Message(
                id=str(uuid4()),
                room_id=room.id,
                sender_id=str(test_user_ids["current_user"]),
                content="Hello!",
                status=MessageStatus.SENT,
                created_at=datetime.utcnow(),
            )
        ]

        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.get_messages_by_room_id",
            new_callable=AsyncMock,
        ) as mock_get_messages, patch(
            "app.modules.social.infrastructure.repositories.friendship_repository_impl.FriendshipRepositoryImpl.are_friends",
            new_callable=AsyncMock,
        ) as mock_are_friends, patch(
            "app.modules.social.infrastructure.repositories.friendship_repository_impl.FriendshipRepositoryImpl.is_blocked",
            new_callable=AsyncMock,
        ) as mock_is_blocked:
            mock_get_room.return_value = room
            mock_get_messages.return_value = messages
            mock_are_friends.return_value = True
            mock_is_blocked.return_value = False

            # Act
            response = client.get(f"/api/v1/chats/{room.id}/messages")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert "messages" in data
            assert len(data["messages"]) == 1
            assert data["messages"][0]["content"] == "Hello!"

    @pytest.mark.asyncio
    async def test_send_message_success(
        self, mock_auth, mock_db_session, test_user_ids, test_chat_rooms
    ):
        """Test successfully sending a message"""
        # Arrange
        room = test_chat_rooms[0]
        message_content = "Test message"

        with patch(
            "app.modules.social.infrastructure.repositories.chat_room_repository_impl.ChatRoomRepositoryImpl.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_room, patch(
            "app.modules.social.infrastructure.repositories.message_repository_impl.MessageRepositoryImpl.create",
            new_callable=AsyncMock,
        ) as mock_create_message, patch(
            "app.modules.social.infrastructure.repositories.friendship_repository_impl.FriendshipRepositoryImpl.are_friends",
            new_callable=AsyncMock,
        ) as mock_are_friends, patch(
            "app.modules.social.infrastructure.repositories.friendship_repository_impl.FriendshipRepositoryImpl.is_blocked",
            new_callable=AsyncMock,
        ) as mock_is_blocked, patch(
            "app.modules.social.presentation.routers.chat_router.get_fcm_service"
        ):
            mock_get_room.return_value = room
            mock_are_friends.return_value = True
            mock_is_blocked.return_value = False

            # Mock create to return a message
            def create_message(msg):
                return msg

            mock_create_message.side_effect = create_message

            # Act
            response = client.post(
                f"/api/v1/chats/{room.id}/messages", json={"content": message_content}
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert data["content"] == message_content
            assert data["room_id"] == room.id
            mock_create_message.assert_called_once()
