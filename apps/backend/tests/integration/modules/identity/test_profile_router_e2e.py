"""
Integration E2E tests for Profile Router

Tests the profile management endpoints:
- GET /profile/me - Get current user's profile
- PUT /profile/me - Update current user's profile
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import UUID

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.modules.identity.presentation.dependencies.auth_deps import get_current_user


class TestProfileRouterE2E:
    """E2E tests for Profile Router endpoints"""

    @pytest_asyncio.fixture
    async def test_user_with_profile(self, db_session) -> UUID:
        """Create test user with profile and return user ID"""
        import uuid
        unique_id = str(uuid.uuid4())
        
        # Create user
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": f"test_profile_{unique_id}",
                "email": f"profile_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        
        # Create profile
        await db_session.execute(
            text("""
                INSERT INTO profiles (
                    user_id, nickname, avatar_url, bio, region,
                    preferences, privacy_flags
                )
                VALUES (
                    :user_id, :nickname, :avatar_url, :bio, :region,
                    :preferences, :privacy_flags
                )
            """),
            {
                "user_id": str(user_id),
                "nickname": "Test User",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Test bio",
                "region": "TW",
                "preferences": "{}",
                "privacy_flags": '{"show_online": true, "allow_stranger_chat": true}'
            }
        )
        await db_session.flush()
        
        return user_id

    @pytest.fixture
    def authenticated_client(self, test_user_with_profile, db_session):
        """Provide authenticated test client"""
        def override_get_current_user():
            return test_user_with_profile

        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[get_current_user] = override_get_current_user
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

    def test_get_my_profile_success(self, authenticated_client):
        """Test getting current user's profile successfully"""
        response = authenticated_client.get("/api/v1/profile/me")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["nickname"] == "Test User"
        assert data["avatar_url"] == "https://example.com/avatar.jpg"
        assert data["bio"] == "Test bio"
        assert data["region"] == "TW"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_my_profile_unauthorized(self, unauthenticated_client):
        """Test getting profile without authentication returns 401"""
        response = unauthenticated_client.get("/api/v1/profile/me")

        assert response.status_code == 401

    def test_update_my_profile_nickname(self, authenticated_client):
        """Test updating profile nickname"""
        payload = {
            "nickname": "Updated Nickname"
        }

        response = authenticated_client.put("/api/v1/profile/me", json=payload)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["nickname"] == "Updated Nickname"

    def test_update_my_profile_multiple_fields(self, authenticated_client):
        """Test updating multiple profile fields at once"""
        payload = {
            "nickname": "New Nickname",
            "bio": "New bio text",
            "region": "KR"
        }

        response = authenticated_client.put("/api/v1/profile/me", json=payload)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["nickname"] == "New Nickname"
        assert data["bio"] == "New bio text"
        assert data["region"] == "KR"

    def test_update_my_profile_unauthorized(self, unauthenticated_client):
        """Test updating profile without authentication"""
        payload = {
            "nickname": "Should Fail"
        }

        response = unauthenticated_client.put("/api/v1/profile/me", json=payload)

        assert response.status_code == 401

    def test_update_my_profile_with_preferences(self, authenticated_client):
        """Test updating profile with preferences"""
        payload = {
            "preferences": {
                "language": "zh-TW",
                "theme": "dark"
            }
        }

        response = authenticated_client.put("/api/v1/profile/me", json=payload)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["preferences"]["language"] == "zh-TW"
        assert data["preferences"]["theme"] == "dark"

    def test_update_my_profile_with_privacy_flags(self, authenticated_client):
        """Test updating profile with privacy flags"""
        payload = {
            "privacy_flags": {
                "show_online": False,
                "allow_stranger_chat": False
            }
        }

        response = authenticated_client.put("/api/v1/profile/me", json=payload)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["privacy_flags"]["show_online"] is False
        assert data["privacy_flags"]["allow_stranger_chat"] is False

    def test_update_my_profile_empty_payload(self, authenticated_client):
        """Test updating profile with empty payload (should succeed with no changes)"""
        payload = {}

        response = authenticated_client.put("/api/v1/profile/me", json=payload)

        assert response.status_code == 200
        data = response.json()["data"]
        # Original values should be preserved
        assert data["nickname"] == "Test User"
