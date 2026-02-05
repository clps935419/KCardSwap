"""
Integration E2E tests for Friends Router

Tests the friends management endpoints:
- POST /friends/block - Block a user
- POST /friends/unblock - Unblock a user
"""

from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id


class TestFriendsRouterE2E:
    """E2E tests for Friends Router endpoints"""

    @pytest_asyncio.fixture
    async def test_user1(self, db_session) -> UUID:
        """Create first test user"""
        import uuid

        unique_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """
            ),
            {
                "id": user_id,
                "google_id": f"test_friend1_{unique_id}",
                "email": f"friend1_{unique_id}@test.com",
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
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """
            ),
            {
                "id": user_id,
                "google_id": f"test_friend2_{unique_id}",
                "email": f"friend2_{unique_id}@test.com",
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

    def test_block_user_success(self, authenticated_client_user1, test_user2):
        """Test blocking a user successfully"""
        payload = {"user_id": str(test_user2)}

        response = authenticated_client_user1.post(
            "/api/v1/friends/block", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "blocked" in data["message"].lower()

    def test_block_user_invalid_id(self, authenticated_client_user1):
        """Test blocking with invalid user ID format"""
        payload = {"user_id": "not-a-valid-uuid"}

        response = authenticated_client_user1.post(
            "/api/v1/friends/block", json=payload
        )

        assert response.status_code == 400

    def test_block_user_self(self, authenticated_client_user1, test_user1):
        """Test blocking yourself (should fail)"""
        payload = {"user_id": str(test_user1)}

        response = authenticated_client_user1.post(
            "/api/v1/friends/block", json=payload
        )

        # Should return 400 depending on validation
        assert response.status_code == 400

    def test_block_user_unauthorized(self, unauthenticated_client, test_user2):
        """Test blocking without authentication"""
        payload = {"user_id": str(test_user2)}

        response = unauthenticated_client.post("/api/v1/friends/block", json=payload)

        assert response.status_code == 401

    def test_unblock_user_success(self, authenticated_client_user1, test_user2):
        """Test unblocking a user successfully"""
        # First block the user
        block_payload = {"user_id": str(test_user2)}
        authenticated_client_user1.post("/api/v1/friends/block", json=block_payload)

        # Then unblock
        unblock_payload = {"user_id": str(test_user2)}
        response = authenticated_client_user1.post(
            "/api/v1/friends/unblock", json=unblock_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "unblock" in data["message"].lower()

    def test_unblock_user_not_blocked(self, authenticated_client_user1, test_user2):
        """Test unblocking a user who is not blocked"""
        payload = {"user_id": str(test_user2)}

        response = authenticated_client_user1.post(
            "/api/v1/friends/unblock", json=payload
        )

        # Should succeed or return 400 depending on implementation
        assert response.status_code in [200, 400]

    def test_unblock_user_invalid_id(self, authenticated_client_user1):
        """Test unblocking with invalid user ID format"""
        payload = {"user_id": "not-a-valid-uuid"}

        response = authenticated_client_user1.post(
            "/api/v1/friends/unblock", json=payload
        )

        assert response.status_code == 400

    def test_unblock_user_unauthorized(self, unauthenticated_client, test_user2):
        """Test unblocking without authentication"""
        payload = {"user_id": str(test_user2)}

        response = unauthenticated_client.post("/api/v1/friends/unblock", json=payload)

        assert response.status_code == 401

    def test_block_missing_user_id(self, authenticated_client_user1):
        """Test blocking without providing user_id"""
        payload = {}

        response = authenticated_client_user1.post(
            "/api/v1/friends/block", json=payload
        )

        assert response.status_code == 400

    def test_unblock_missing_user_id(self, authenticated_client_user1):
        """Test unblocking without providing user_id"""
        payload = {}

        response = authenticated_client_user1.post(
            "/api/v1/friends/unblock", json=payload
        )

        assert response.status_code == 400
