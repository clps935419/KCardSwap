"""
Integration tests for Profile Flow with Real Database

Tests complete profile management flow using real database with automatic rollback.
Based on actual Profile API endpoints: GET /profile/me and PUT /profile/me
"""

from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestProfileFlowWithRealDatabase:
    """Integration tests for profile flow using real database"""

    @pytest_asyncio.fixture
    async def test_user(self, db_session) -> UUID:
        """Create test user in database"""
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": "profile_test_user",
                "email": "profileuser@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest_asyncio.fixture
    async def test_user_with_profile(self, db_session, test_user) -> tuple[UUID, UUID]:
        """Create test user with profile in database"""
        # Create profile for user
        result = await db_session.execute(
            text("""
                INSERT INTO profiles (user_id, nickname, bio, region, preferences, privacy_flags)
                VALUES (:user_id, :nickname, :bio, :region, :preferences, :privacy_flags)
                RETURNING id
            """),
            {
                "user_id": test_user,
                "nickname": "TestNick",
                "bio": "Test bio",
                "region": "TW-TPE",
                "preferences": {"theme": "light"},
                "privacy_flags": {"nearby_visible": True, "show_online": True, "allow_stranger_chat": True}
            }
        )
        profile_id = result.scalar()
        await db_session.flush()
        return test_user, profile_id

    @pytest.fixture
    def authenticated_client(self, test_user, db_session):
        """Provide authenticated client"""
        async def override_get_current_user_id():
            return test_user
        
        async def override_get_db_session():
            return db_session
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = override_get_db_session
        
        yield client
        
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_profile_requires_authentication(self):
        """Test that getting profile requires authentication"""
        response = client.get("/api/v1/profile/me")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_update_profile_requires_authentication(self):
        """Test that updating profile requires authentication"""
        response = client.put("/api/v1/profile/me", json={"nickname": "NewNick"})
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_profile_success(
        self,
        authenticated_client,
        test_user_with_profile,
        db_session
    ):
        """Test successful profile retrieval with valid authentication"""
        user_id, profile_id = test_user_with_profile
        
        response = authenticated_client.get("/api/v1/profile/me")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "data" in data
        assert "error" in data
        assert data["error"] is None
        
        # Check profile data
        profile = data["data"]
        assert "id" in profile
        assert "user_id" in profile
        assert profile["user_id"] == str(user_id)
        assert profile["nickname"] == "TestNick"
        assert profile["bio"] == "Test bio"
        assert profile["region"] == "TW-TPE"
        assert "preferences" in profile
        assert "privacy_flags" in profile
        assert "created_at" in profile
        assert "updated_at" in profile

    @pytest.mark.asyncio
    async def test_get_profile_not_found(
        self,
        authenticated_client,
        test_user,
        db_session
    ):
        """Test profile retrieval when profile doesn't exist"""
        # test_user exists but has no profile
        response = authenticated_client.get("/api/v1/profile/me")
        
        # Should return 404 NOT_FOUND
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_update_profile_full_update(
        self,
        authenticated_client,
        test_user_with_profile,
        db_session
    ):
        """Test successful full profile update"""
        user_id, profile_id = test_user_with_profile
        
        update_data = {
            "nickname": "UpdatedNick",
            "bio": "Updated bio",
            "avatar_url": "https://example.com/avatar.jpg",
            "region": "TW-KHH",
            "preferences": {"theme": "dark", "language": "zh-TW"},
            "privacy_flags": {
                "nearby_visible": False,
                "show_online": True,
                "allow_stranger_chat": False
            }
        }
        
        response = authenticated_client.put("/api/v1/profile/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        
        profile = data["data"]
        assert profile["nickname"] == "UpdatedNick"
        assert profile["bio"] == "Updated bio"
        assert profile["avatar_url"] == "https://example.com/avatar.jpg"
        assert profile["region"] == "TW-KHH"
        assert profile["preferences"]["theme"] == "dark"
        assert profile["privacy_flags"]["nearby_visible"] is False

    @pytest.mark.asyncio
    async def test_update_profile_partial_update(
        self,
        authenticated_client,
        test_user_with_profile,
        db_session
    ):
        """Test successful partial profile update - only nickname and bio"""
        user_id, profile_id = test_user_with_profile
        
        # Get original profile
        original_response = authenticated_client.get("/api/v1/profile/me")
        original_profile = original_response.json()["data"]
        
        # Update only nickname and bio
        update_data = {
            "nickname": "NewNickname",
            "bio": "New bio text"
        }
        
        response = authenticated_client.put("/api/v1/profile/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        profile = data["data"]
        
        # Check updated fields
        assert profile["nickname"] == "NewNickname"
        assert profile["bio"] == "New bio text"
        
        # Check unchanged fields
        assert profile["region"] == original_profile["region"]
        assert profile["preferences"] == original_profile["preferences"]

    @pytest.mark.asyncio
    async def test_update_profile_nickname_only(
        self,
        authenticated_client,
        test_user_with_profile,
        db_session
    ):
        """Test updating only nickname"""
        user_id, profile_id = test_user_with_profile
        
        update_data = {"nickname": "CoolNickname"}
        
        response = authenticated_client.put("/api/v1/profile/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["nickname"] == "CoolNickname"

    @pytest.mark.asyncio
    async def test_update_profile_privacy_flags(
        self,
        authenticated_client,
        test_user_with_profile,
        db_session
    ):
        """Test updating privacy flags"""
        user_id, profile_id = test_user_with_profile
        
        update_data = {
            "privacy_flags": {
                "nearby_visible": False,
                "show_online": False,
                "allow_stranger_chat": False
            }
        }
        
        response = authenticated_client.put("/api/v1/profile/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        privacy_flags = data["data"]["privacy_flags"]
        assert privacy_flags["nearby_visible"] is False
        assert privacy_flags["show_online"] is False
        assert privacy_flags["allow_stranger_chat"] is False

    @pytest.mark.asyncio
    async def test_complete_profile_lifecycle(
        self,
        authenticated_client,
        test_user_with_profile,
        db_session
    ):
        """Test complete profile lifecycle: get, update, verify"""
        user_id, profile_id = test_user_with_profile
        
        # Step 1: Get initial profile
        get_response = authenticated_client.get("/api/v1/profile/me")
        assert get_response.status_code == 200
        initial_profile = get_response.json()["data"]
        assert initial_profile["nickname"] == "TestNick"
        
        # Step 2: Update profile
        update_data = {
            "nickname": "MyNewNickname",
            "bio": "My new bio",
            "region": "TW-TXG"
        }
        update_response = authenticated_client.put("/api/v1/profile/me", json=update_data)
        assert update_response.status_code == 200
        
        # Step 3: Verify updates persisted
        verify_response = authenticated_client.get("/api/v1/profile/me")
        assert verify_response.status_code == 200
        updated_profile = verify_response.json()["data"]
        assert updated_profile["nickname"] == "MyNewNickname"
        assert updated_profile["bio"] == "My new bio"
        assert updated_profile["region"] == "TW-TXG"
        assert updated_profile["id"] == initial_profile["id"]  # Same profile ID

    @pytest.mark.asyncio
    async def test_profile_response_structure(
        self,
        authenticated_client,
        test_user_with_profile,
        db_session
    ):
        """Test that profile response matches the expected schema structure"""
        user_id, profile_id = test_user_with_profile
        
        response = authenticated_client.get("/api/v1/profile/me")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check wrapper structure
        assert "data" in data
        assert "error" in data
        assert data["error"] is None
        
        # Check profile data structure
        profile = data["data"]
        required_fields = [
            "id", "user_id", "nickname", "bio",
            "region", "preferences", "privacy_flags",
            "created_at", "updated_at"
        ]
        for field in required_fields:
            assert field in profile, f"Missing required field: {field}"
        
        # Check types
        assert isinstance(profile["preferences"], dict)
        assert isinstance(profile["privacy_flags"], dict)

    @pytest.mark.asyncio
    async def test_profile_endpoint_exists(self):
        """Verify profile endpoints are registered"""
        # Test GET endpoint exists (returns 401/403, not 404)
        response = client.get("/api/v1/profile/me")
        assert response.status_code != 404
        
        # Test PUT endpoint exists (returns 401/403, not 404)
        response = client.put("/api/v1/profile/me", json={})
        assert response.status_code != 404
