"""
Integration E2E tests for Threads Router

Tests the threads management endpoints:
- GET /threads - Get threads list
- GET /threads/{thread_id}/messages - Get thread messages
- POST /threads/{thread_id}/messages - Send message in thread
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import UUID, uuid4

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import require_user as get_current_user_id_alias


class TestThreadsRouterE2E:
    """E2E tests for Threads Router endpoints"""

    @pytest_asyncio.fixture
    async def test_user1(self, db_session) -> UUID:
        """Create first test user"""
        import uuid
        unique_id = str(uuid.uuid4())
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": f"test_thread1_{unique_id}",
                "email": f"thread1_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest_asyncio.fixture
    async def test_user2(self, db_session) -> UUID:
        """Create second test user"""
        import uuid
        unique_id = str(uuid.uuid4())
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": f"test_thread2_{unique_id}",
                "email": f"thread2_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest.fixture
    def authenticated_client_user1(self, test_user1, db_session):
        """Provide authenticated test client for user1"""
        def override_require_user():
            return test_user1

        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[get_current_user_id_alias] = override_require_user
        app.dependency_overrides[get_db_session] = override_get_db_session

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    @pytest.fixture
    def unauthenticated_client(self, db_session):
        """Provide unauthenticated test client"""
        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[get_db_session] = override_get_db_session

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    def test_get_threads_empty(self, authenticated_client_user1):
        """Test getting threads when user has none"""
        response = authenticated_client_user1.get("/api/v1/threads")

        assert response.status_code == 200
        data = response.json()
        assert "threads" in data
        assert isinstance(data["threads"], list)

    def test_get_threads_unauthorized(self, unauthenticated_client):
        """Test getting threads without authentication"""
        response = unauthenticated_client.get("/api/v1/threads")

        assert response.status_code == 401

    def test_get_threads_with_pagination(self, authenticated_client_user1):
        """Test getting threads with pagination parameters"""
        response = authenticated_client_user1.get("/api/v1/threads?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert "threads" in data
        assert "total" in data

    @pytest_asyncio.fixture
    async def test_thread(self, test_user1, test_user2, db_session) -> str:
        """Create a test thread between user1 and user2"""
        thread_id = str(uuid4())
        await db_session.execute(
            text("""
                INSERT INTO threads (id, user_a_id, user_b_id, created_at, updated_at)
                VALUES (:id, :user_a_id, :user_b_id, NOW(), NOW())
            """),
            {
                "id": thread_id,
                "user_a_id": str(test_user1),
                "user_b_id": str(test_user2)
            }
        )
        await db_session.flush()
        return thread_id

    def test_get_threads_with_thread(self, authenticated_client_user1, test_thread):
        """Test getting threads when user has threads"""
        response = authenticated_client_user1.get("/api/v1/threads")

        assert response.status_code == 200
        data = response.json()
        assert "threads" in data
        assert len(data["threads"]) > 0

    def test_get_thread_messages_not_found(self, authenticated_client_user1):
        """Test getting messages from non-existent thread"""
        fake_thread_id = str(uuid4())
        response = authenticated_client_user1.get(f"/api/v1/threads/{fake_thread_id}/messages")

        assert response.status_code in [403, 404]

    def test_get_thread_messages_unauthorized(self, unauthenticated_client, test_thread):
        """Test getting thread messages without authentication"""
        response = unauthenticated_client.get(f"/api/v1/threads/{test_thread}/messages")

        assert response.status_code == 401

    def test_get_thread_messages_success(self, authenticated_client_user1, test_thread):
        """Test getting messages from a thread successfully"""
        response = authenticated_client_user1.get(f"/api/v1/threads/{test_thread}/messages")

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)

    def test_get_thread_messages_with_pagination(
        self, authenticated_client_user1, test_thread
    ):
        """Test getting thread messages with pagination"""
        response = authenticated_client_user1.get(
            f"/api/v1/threads/{test_thread}/messages?limit=20&offset=0"
        )

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data

    def test_send_message_thread_not_found(self, authenticated_client_user1):
        """Test sending message to non-existent thread"""
        fake_thread_id = str(uuid4())
        payload = {
            "content": "Hello"
        }
        response = authenticated_client_user1.post(
            f"/api/v1/threads/{fake_thread_id}/messages",
            json=payload
        )

        assert response.status_code == 403

    def test_send_message_unauthorized(self, unauthenticated_client, test_thread):
        """Test sending message without authentication"""
        payload = {
            "content": "Hello"
        }
        response = unauthenticated_client.post(
            f"/api/v1/threads/{test_thread}/messages",
            json=payload
        )

        assert response.status_code == 401

    def test_send_message_success(self, authenticated_client_user1, test_thread):
        """Test sending message in thread successfully"""
        payload = {
            "content": "This is a test message in thread"
        }
        response = authenticated_client_user1.post(
            f"/api/v1/threads/{test_thread}/messages",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == payload["content"]
        assert "id" in data
        assert "sender_id" in data
        assert "thread_id" in data
        assert "created_at" in data

    def test_send_message_with_post_reference(
        self, authenticated_client_user1, test_thread
    ):
        """Test sending message with post reference"""
        payload = {
            "content": "Check out this post",
            "post_id": str(uuid4())
        }
        response = authenticated_client_user1.post(
            f"/api/v1/threads/{test_thread}/messages",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == payload["content"]
        assert "post_id" in data

    def test_send_message_empty_content(self, authenticated_client_user1, test_thread):
        """Test sending message with empty content"""
        payload = {
            "content": ""
        }
        response = authenticated_client_user1.post(
            f"/api/v1/threads/{test_thread}/messages",
            json=payload
        )

        assert response.status_code in [400, 422]

    def test_send_message_missing_content(self, authenticated_client_user1, test_thread):
        """Test sending message without content field"""
        payload = {}
        response = authenticated_client_user1.post(
            f"/api/v1/threads/{test_thread}/messages",
            json=payload
        )

        assert response.status_code == 400

    @pytest_asyncio.fixture
    async def test_thread_with_messages(self, test_user1, test_user2, test_thread, db_session):
        """Create test messages in the thread"""
        for i in range(3):
            message_id = str(uuid4())
            await db_session.execute(
                text("""
                    INSERT INTO thread_messages (
                        id, thread_id, sender_id, content, created_at
                    )
                    VALUES (:id, :thread_id, :sender_id, :content, NOW())
                """),
                {
                    "id": message_id,
                    "thread_id": test_thread,
                    "sender_id": str(test_user1),
                    "content": f"Test message {i+1}"
                }
            )
        await db_session.flush()

    def test_get_thread_messages_with_content(
        self, authenticated_client_user1, test_thread, test_thread_with_messages
    ):
        """Test getting thread messages with actual content"""
        response = authenticated_client_user1.get(f"/api/v1/threads/{test_thread}/messages")

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) >= 3
        
        # Verify message structure
        message = data["messages"][0]
        assert "id" in message
        assert "content" in message
        assert "sender_id" in message
        assert "created_at" in message
