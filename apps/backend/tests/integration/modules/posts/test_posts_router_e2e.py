"""
Integration E2E tests for Posts Router

Tests the posts management endpoints:
- POST /posts - Create post
- GET /posts - List posts
- POST /posts/{post_id}/close - Close post
- POST /posts/{post_id}/like - Toggle like
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import UUID, uuid4

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import require_user


class TestPostsRouterE2E:
    """E2E tests for Posts Router endpoints"""

    @pytest_asyncio.fixture
    async def test_user(self, db_session) -> UUID:
        """Create test user and return user ID"""
        import uuid
        unique_id = str(uuid.uuid4())
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": f"test_posts_{unique_id}",
                "email": f"posts_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest.fixture
    def authenticated_client(self, test_user, db_session):
        """Provide authenticated test client"""
        def override_require_user():
            return test_user

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

    # ===== Create Post Tests =====

    def test_create_post_global_success(self, authenticated_client):
        """Test creating a global post successfully"""
        payload = {
            "scope": "global",
            "category": "trade",
            "title": "Looking for BTS cards",
            "content": "I have extra Jungkook cards to trade",
            "idol": "Jungkook",
            "idol_group": "BTS"
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["scope"] == "global"
        assert data["category"] == "trade"
        assert data["title"] == payload["title"]
        assert data["city_code"] is None

    def test_create_post_city_success(self, authenticated_client):
        """Test creating a city post successfully"""
        payload = {
            "scope": "city",
            "city_code": "TPE",
            "category": "sale",
            "title": "Selling IU photocards",
            "content": "Brand new IU photocards for sale",
            "idol": "IU",
            "idol_group": "Solo"
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["scope"] == "city"
        assert data["city_code"] == "TPE"
        assert data["category"] == "sale"

    def test_create_post_missing_required_fields(self, authenticated_client):
        """Test creating post with missing required fields"""
        payload = {
            "scope": "global",
            # Missing category, title, content
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        assert response.status_code == 400

    def test_create_post_city_without_city_code(self, authenticated_client):
        """Test creating city post without city_code"""
        payload = {
            "scope": "city",
            # Missing city_code
            "category": "trade",
            "title": "Test post",
            "content": "Content"
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        # Should fail validation
        assert response.status_code in [400, 422]

    def test_create_post_global_with_city_code(self, authenticated_client):
        """Test creating global post with city_code (should fail)"""
        payload = {
            "scope": "global",
            "city_code": "TPE",  # Should not be allowed for global
            "category": "trade",
            "title": "Test post",
            "content": "Content"
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        # Should fail validation
        assert response.status_code in [400, 422]

    def test_create_post_unauthorized(self, unauthenticated_client):
        """Test creating post without authentication"""
        payload = {
            "scope": "global",
            "category": "trade",
            "title": "Test",
            "content": "Test"
        }

        response = unauthenticated_client.post("/api/v1/posts", json=payload)

        assert response.status_code == 401

    # ===== List Posts Tests =====

    def test_list_posts_global_view(self, authenticated_client):
        """Test listing posts in global view (no city filter)"""
        response = authenticated_client.get("/api/v1/posts")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "posts" in data
        assert "total" in data
        assert isinstance(data["posts"], list)

    def test_list_posts_city_view(self, authenticated_client):
        """Test listing posts for a specific city"""
        response = authenticated_client.get("/api/v1/posts?city_code=TPE")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "posts" in data

    def test_list_posts_with_category_filter(self, authenticated_client):
        """Test listing posts with category filter"""
        response = authenticated_client.get("/api/v1/posts?category=trade")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "posts" in data

    def test_list_posts_with_pagination(self, authenticated_client):
        """Test listing posts with pagination parameters"""
        response = authenticated_client.get("/api/v1/posts?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "posts" in data

    def test_list_posts_unauthorized(self, unauthenticated_client):
        """Test listing posts without authentication"""
        response = unauthenticated_client.get("/api/v1/posts")

        assert response.status_code == 401

    # ===== Close Post Tests =====

    @pytest_asyncio.fixture
    async def test_post(self, test_user, db_session) -> UUID:
        """Create a test post"""
        post_id = uuid4()
        await db_session.execute(
            text("""
                INSERT INTO posts (
                    id, owner_id, scope, category, title, content, 
                    status, created_at, updated_at
                )
                VALUES (
                    :id, :owner_id, :scope, :category, :title, :content,
                    :status, NOW(), NOW()
                )
            """),
            {
                "id": str(post_id),
                "owner_id": str(test_user),
                "scope": "global",
                "category": "trade",
                "title": "Test Post",
                "content": "Test Content",
                "status": "open"
            }
        )
        await db_session.flush()
        return post_id

    def test_close_post_success(self, authenticated_client, test_post):
        """Test closing a post successfully"""
        response = authenticated_client.post(f"/api/v1/posts/{test_post}/close")

        assert response.status_code == 204

    def test_close_post_not_found(self, authenticated_client):
        """Test closing non-existent post"""
        fake_id = uuid4()
        response = authenticated_client.post(f"/api/v1/posts/{fake_id}/close")

        assert response.status_code == 404

    def test_close_post_unauthorized(self, unauthenticated_client, test_post):
        """Test closing post without authentication"""
        response = unauthenticated_client.post(f"/api/v1/posts/{test_post}/close")

        assert response.status_code == 401

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
                "google_id": f"test_posts2_{unique_id}",
                "email": f"posts2_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    def test_close_post_not_owner(self, test_user2, test_post, db_session):
        """Test closing post by non-owner (should fail)"""
        def override_require_user():
            return test_user2

        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[require_user] = override_require_user
        app.dependency_overrides[get_db_session] = override_get_db_session

        try:
            client = TestClient(app)
            response = client.post(f"/api/v1/posts/{test_post}/close")

            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()

    # ===== Toggle Like Tests =====

    def test_toggle_like_success(self, authenticated_client, test_post):
        """Test toggling like on a post"""
        response = authenticated_client.post(f"/api/v1/posts/{test_post}/like")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "liked" in data
        assert "like_count" in data
        assert isinstance(data["liked"], bool)
        assert isinstance(data["like_count"], int)

    def test_toggle_like_twice(self, authenticated_client, test_post):
        """Test toggling like twice (like then unlike)"""
        # First like
        response1 = authenticated_client.post(f"/api/v1/posts/{test_post}/like")
        assert response1.status_code == 200
        data1 = response1.json()["data"]
        first_liked = data1["liked"]

        # Second like (should toggle)
        response2 = authenticated_client.post(f"/api/v1/posts/{test_post}/like")
        assert response2.status_code == 200
        data2 = response2.json()["data"]
        second_liked = data2["liked"]

        # Should be opposite
        assert first_liked != second_liked

    def test_toggle_like_not_found(self, authenticated_client):
        """Test toggling like on non-existent post"""
        fake_id = uuid4()
        response = authenticated_client.post(f"/api/v1/posts/{fake_id}/like")

        assert response.status_code == 404

    def test_toggle_like_unauthorized(self, unauthenticated_client, test_post):
        """Test toggling like without authentication"""
        response = unauthenticated_client.post(f"/api/v1/posts/{test_post}/like")

        assert response.status_code == 401
