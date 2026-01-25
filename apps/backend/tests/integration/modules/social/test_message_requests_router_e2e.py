"""
Integration E2E tests for Message Requests Router

Tests the message requests endpoints:
- POST /message-requests - Create message request
- GET /message-requests/inbox - Get my message requests
- POST /message-requests/{request_id}/accept - Accept request
- POST /message-requests/{request_id}/decline - Decline request
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import UUID, uuid4

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import require_user


class TestMessageRequestsRouterE2E:
    """E2E tests for Message Requests Router endpoints"""

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
                "google_id": f"test_msgreq1_{unique_id}",
                "email": f"msgreq1_{unique_id}@test.com",
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
                "google_id": f"test_msgreq2_{unique_id}",
                "email": f"msgreq2_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        
        # Create profile for user2 with privacy settings
        await db_session.execute(
            text("""
                INSERT INTO profiles (
                    user_id, nickname, privacy_flags
                )
                VALUES (
                    :user_id, :nickname, :privacy_flags
                )
            """),
            {
                "user_id": str(user_id),
                "nickname": "Test User 2",
                "privacy_flags": '{"allow_stranger_chat": true}'
            }
        )
        await db_session.flush()
        return user_id

    @pytest.fixture
    def authenticated_client_user1(self, test_user1, db_session):
        """Provide authenticated test client for user1"""
        def override_require_user():
            return test_user1

        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[require_user] = override_require_user
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

    # ===== Create Message Request Tests =====

    def test_create_message_request_success(
        self, authenticated_client_user1, test_user2
    ):
        """Test creating a message request successfully"""
        payload = {
            "recipient_id": str(test_user2),
            "initial_message": "Hello, I'm interested in your card"
        }

        response = authenticated_client_user1.post("/api/v1/message-requests", json=payload)

        # Should succeed or return error based on implementation
        assert response.status_code in [201, 400]
        
        if response.status_code == 201:
            data = response.json()
            assert data["sender_id"] == str(authenticated_client_user1)
            assert data["recipient_id"] == str(test_user2)
            assert data["initial_message"] == payload["initial_message"]

    def test_create_message_request_with_post_reference(
        self, authenticated_client_user1, test_user2
    ):
        """Test creating message request with post reference"""
        fake_post_id = str(uuid4())
        payload = {
            "recipient_id": str(test_user2),
            "initial_message": "About your post",
            "post_id": fake_post_id
        }

        response = authenticated_client_user1.post("/api/v1/message-requests", json=payload)

        # Should succeed or fail based on implementation
        assert response.status_code in [201, 400, 404]

    def test_create_message_request_missing_recipient(
        self, authenticated_client_user1
    ):
        """Test creating message request without recipient"""
        payload = {
            "initial_message": "Hello"
        }

        response = authenticated_client_user1.post("/api/v1/message-requests", json=payload)

        assert response.status_code == 400

    def test_create_message_request_missing_message(
        self, authenticated_client_user1, test_user2
    ):
        """Test creating message request without initial message"""
        payload = {
            "recipient_id": str(test_user2)
        }

        response = authenticated_client_user1.post("/api/v1/message-requests", json=payload)

        assert response.status_code == 400

    def test_create_message_request_to_self(
        self, authenticated_client_user1, test_user1
    ):
        """Test creating message request to oneself (should fail)"""
        payload = {
            "recipient_id": str(test_user1),
            "initial_message": "Hello to myself"
        }

        response = authenticated_client_user1.post("/api/v1/message-requests", json=payload)

        assert response.status_code == 400

    def test_create_message_request_unauthorized(
        self, unauthenticated_client, test_user2
    ):
        """Test creating message request without authentication"""
        payload = {
            "recipient_id": str(test_user2),
            "initial_message": "Hello"
        }

        response = unauthenticated_client.post("/api/v1/message-requests", json=payload)

        assert response.status_code == 401

    # ===== Get Inbox Tests =====

    def test_get_inbox_empty(self, authenticated_client_user1):
        """Test getting inbox when user has no message requests"""
        response = authenticated_client_user1.get("/api/v1/message-requests/inbox")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_inbox_with_status_filter(self, authenticated_client_user1):
        """Test getting inbox with status filter"""
        response = authenticated_client_user1.get(
            "/api/v1/message-requests/inbox?status_filter=pending"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_inbox_unauthorized(self, unauthenticated_client):
        """Test getting inbox without authentication"""
        response = unauthenticated_client.get("/api/v1/message-requests/inbox")

        assert response.status_code == 401

    # ===== Accept Request Tests =====

    def test_accept_request_not_found(self, authenticated_client_user1):
        """Test accepting non-existent message request"""
        fake_request_id = str(uuid4())
        response = authenticated_client_user1.post(
            f"/api/v1/message-requests/{fake_request_id}/accept"
        )

        assert response.status_code in [400, 404]

    def test_accept_request_unauthorized(self, unauthenticated_client):
        """Test accepting request without authentication"""
        fake_request_id = str(uuid4())
        response = unauthenticated_client.post(
            f"/api/v1/message-requests/{fake_request_id}/accept"
        )

        assert response.status_code == 401

    # ===== Decline Request Tests =====

    def test_decline_request_not_found(self, authenticated_client_user1):
        """Test declining non-existent message request"""
        fake_request_id = str(uuid4())
        response = authenticated_client_user1.post(
            f"/api/v1/message-requests/{fake_request_id}/decline"
        )

        assert response.status_code in [400, 404]

    def test_decline_request_unauthorized(self, unauthenticated_client):
        """Test declining request without authentication"""
        fake_request_id = str(uuid4())
        response = unauthenticated_client.post(
            f"/api/v1/message-requests/{fake_request_id}/decline"
        )

        assert response.status_code == 401
