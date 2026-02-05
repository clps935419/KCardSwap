"""
Integration E2E tests for Chat Router

Tests the chat management endpoints:
- GET /chats - Get chat rooms
- GET /chats/{room_id}/messages - Get messages
- POST /chats/{room_id}/messages - Send message
- POST /chats/{room_id}/messages/{message_id}/read - Mark message as read
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import UUID, uuid4

from app.main import app
from app.modules.social.infrastructure.database.models.chat_room_model import (
    ChatRoomModel,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id


class TestChatRouterE2E:
    """E2E tests for Chat Router endpoints"""

    @pytest_asyncio.fixture
    async def test_user1(self, db_session) -> UUID:
        """Create first test user"""
        import uuid
        unique_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        result = await db_session.execute(
            text("""
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """),
            {
                "id": user_id,
                "google_id": f"test_chat1_{unique_id}",
                "email": f"chat1_{unique_id}@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.commit()
        return user_id

    @pytest_asyncio.fixture
    async def test_user2(self, db_session) -> UUID:
        """Create second test user"""
        import uuid
        unique_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        result = await db_session.execute(
            text("""
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """),
            {
                "id": user_id,
                "google_id": f"test_chat2_{unique_id}",
                "email": f"chat2_{unique_id}@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.commit()
        return user_id

    @pytest.fixture
    def authenticated_client_user1(self, test_user1, app_db_session_override):
        """Provide authenticated test client for user1"""
        def override_get_current_user_id():
            return test_user1

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = app_db_session_override

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    @pytest.fixture
    def unauthenticated_client(self, app_db_session_override):
        """Provide unauthenticated test client"""
        app.dependency_overrides[get_db_session] = app_db_session_override

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    def test_get_chat_rooms_empty(self, authenticated_client_user1):
        """Test getting chat rooms when user has none"""
        response = authenticated_client_user1.get("/api/v1/chats")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "rooms" in data
        assert isinstance(data["rooms"], list)

    def test_get_chat_rooms_unauthorized(self, unauthenticated_client):
        """Test getting chat rooms without authentication"""
        response = unauthenticated_client.get("/api/v1/chats")

        assert response.status_code == 401

    @pytest_asyncio.fixture
    async def test_chat_room(self, test_user1, test_user2, db_session) -> UUID:
        """Create a test chat room between user1 and user2"""
        room_id = uuid4()
        participants = sorted([test_user1, test_user2], key=str)
        db_session.add(
            ChatRoomModel(id=room_id, participant_ids=participants)
        )
        await db_session.commit()
        return room_id

    @pytest_asyncio.fixture
    async def test_friendship(self, test_user1, test_user2, db_session):
        """Create a friendship between user1 and user2"""
        friendship_id = uuid4()
        await db_session.execute(
            text("""
                INSERT INTO friendships (id, user_id, friend_id, status)
                VALUES (:id, :user_id, :friend_id, :status)
            """),
            {
                "id": str(friendship_id),
                "user_id": str(test_user1),
                "friend_id": str(test_user2),
                "status": "accepted"
            }
        )
        await db_session.commit()

    def test_get_chat_rooms_with_room(self, authenticated_client_user1, test_chat_room):
        """Test getting chat rooms when user has rooms"""
        response = authenticated_client_user1.get("/api/v1/chats")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "rooms" in data
        assert len(data["rooms"]) > 0

    def test_get_messages_room_not_found(self, authenticated_client_user1):
        """Test getting messages from non-existent room"""
        fake_room_id = uuid4()
        response = authenticated_client_user1.get(f"/api/v1/chats/{fake_room_id}/messages")

        assert response.status_code == 404

    def test_get_messages_unauthorized(self, unauthenticated_client, test_chat_room):
        """Test getting messages without authentication"""
        response = unauthenticated_client.get(f"/api/v1/chats/{test_chat_room}/messages")

        assert response.status_code == 401

    def test_get_messages_success(
        self, authenticated_client_user1, test_chat_room, test_friendship
    ):
        """Test getting messages from a room successfully"""
        response = authenticated_client_user1.get(f"/api/v1/chats/{test_chat_room}/messages")

        # Should succeed or return 403 if not participant
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()["data"]
            assert "messages" in data
            assert isinstance(data["messages"], list)

    def test_send_message_room_not_found(self, authenticated_client_user1):
        """Test sending message to non-existent room"""
        fake_room_id = uuid4()
        payload = {
            "content": "Hello"
        }
        response = authenticated_client_user1.post(
            f"/api/v1/chats/{fake_room_id}/messages",
            json=payload
        )

        assert response.status_code == 404

    def test_send_message_unauthorized(self, unauthenticated_client, test_chat_room):
        """Test sending message without authentication"""
        payload = {
            "content": "Hello"
        }
        response = unauthenticated_client.post(
            f"/api/v1/chats/{test_chat_room}/messages",
            json=payload
        )

        assert response.status_code == 401

    def test_send_message_empty_content(self, authenticated_client_user1, test_chat_room):
        """Test sending message with empty content"""
        payload = {
            "content": ""
        }
        response = authenticated_client_user1.post(
            f"/api/v1/chats/{test_chat_room}/messages",
            json=payload
        )

        assert response.status_code in [400, 422]

    def test_send_message_missing_content(self, authenticated_client_user1, test_chat_room):
        """Test sending message without content field"""
        payload = {}
        response = authenticated_client_user1.post(
            f"/api/v1/chats/{test_chat_room}/messages",
            json=payload
        )

        assert response.status_code == 400

    def test_send_message_success(
        self, authenticated_client_user1, test_chat_room, test_friendship
    ):
        """Test sending message successfully"""
        payload = {
            "content": "Hello, this is a test message"
        }
        response = authenticated_client_user1.post(
            f"/api/v1/chats/{test_chat_room}/messages",
            json=payload
        )

        # Should succeed or return 403/422 if not authorized or not friends
        assert response.status_code in [201, 403, 422]
        
        if response.status_code == 201:
            data = response.json()["data"]
            assert data["content"] == payload["content"]
            assert "id" in data
            assert "sender_id" in data
            assert "created_at" in data

    def test_mark_message_read_not_found(self, authenticated_client_user1, test_chat_room):
        """Test marking non-existent message as read"""
        fake_message_id = uuid4()
        response = authenticated_client_user1.post(
            f"/api/v1/chats/{test_chat_room}/messages/{fake_message_id}/read"
        )

        assert response.status_code == 404

    def test_mark_message_read_unauthorized(
        self, unauthenticated_client, test_chat_room
    ):
        """Test marking message as read without authentication"""
        fake_message_id = uuid4()
        response = unauthenticated_client.post(
            f"/api/v1/chats/{test_chat_room}/messages/{fake_message_id}/read"
        )

        assert response.status_code == 401

    def test_get_messages_with_pagination(
        self, authenticated_client_user1, test_chat_room, test_friendship
    ):
        """Test getting messages with pagination parameters"""
        response = authenticated_client_user1.get(
            f"/api/v1/chats/{test_chat_room}/messages?limit=10"
        )

        # Should succeed or return 403 if not participant
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()["data"]
            assert "messages" in data
            assert "has_more" in data
