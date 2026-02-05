"""Integration tests for Posts V2: create and list with scope/category filtering

Tests FR-003, FR-004, FR-005:
- Create global posts
- Create city posts (with city_code)
- List global (includes all posts)
- List city-specific (only city posts)
- Category filtering
- Authentication required
"""

import datetime
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id


class TestPostsCreateAndListV2:
    """Test posts creation and listing with V2 features (scope/category)"""

    @pytest_asyncio.fixture
    async def test_user(self, db_session) -> UUID:
        """Create test user and return user ID"""
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
                "google_id": f"test_posts_v2_{unique_id}",
                "email": f"postsv2_{unique_id}@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.commit()
        return user_id

    @pytest.fixture
    def authenticated_client(self, test_user, app_db_session_override):
        """Provide authenticated test client"""

        def override_get_current_user_id():
            return test_user

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = app_db_session_override

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    def test_create_global_post(self, authenticated_client):
        """Test creating a global post (FR-003)"""
        payload = {
            "scope": "global",
            "category": "trade",
            "title": "Looking for BTS cards globally",
            "content": "I have duplicate Jungkook cards to trade",
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["scope"] == "global"
        assert data["city_code"] is None
        assert data["category"] == "trade"
        assert data["title"] == payload["title"]
        assert data["status"] == "open"

    def test_create_city_post(self, authenticated_client):
        """Test creating a city post with city_code (FR-003, FR-004)"""
        payload = {
            "scope": "city",
            "city_code": "TPE",
            "category": "giveaway",
            "title": "Free cards in Taipei",
            "content": "Giving away duplicate cards",
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["scope"] == "city"
        assert data["city_code"] == "TPE"
        assert data["category"] == "giveaway"

    def test_create_city_post_without_city_code_fails(self, authenticated_client):
        """Test that scope=city requires city_code (FR-004)"""
        payload = {
            "scope": "city",
            "category": "trade",
            "title": "Test",
            "content": "Test content",
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        assert response.status_code in [400, 422]
        assert "city_code" in response.text.lower()

    def test_create_global_post_with_city_code_fails(self, authenticated_client):
        """Test that scope=global must not have city_code (FR-004)"""
        payload = {
            "scope": "global",
            "city_code": "TPE",
            "category": "trade",
            "title": "Test",
            "content": "Test content",
        }

        response = authenticated_client.post("/api/v1/posts", json=payload)

        assert response.status_code in [400, 422]
        assert "city_code" in response.text.lower()

    def test_list_global_includes_all_posts(self, authenticated_client):
        """Test that global list includes all posts (FR-005)"""
        # Create 1 global post
        authenticated_client.post(
            "/api/v1/posts",
            json={
                "scope": "global",
                "category": "trade",
                "title": "Global post",
                "content": "Content",
            },
        )

        # Create 1 city post
        authenticated_client.post(
            "/api/v1/posts",
            json={
                "scope": "city",
                "city_code": "TPE",
                "category": "giveaway",
                "title": "Taipei post",
                "content": "Content",
            },
        )

        # List without city_code (global view)
        response = authenticated_client.get("/api/v1/posts")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total"] >= 2

        # Should include both global and city posts
        scopes = [post["scope"] for post in data["posts"]]
        assert "global" in scopes
        assert "city" in scopes

    def test_list_city_only_includes_city_posts(self, authenticated_client):
        """Test that city list only includes city-specific posts (FR-005)"""
        # Create posts for different cities
        authenticated_client.post(
            "/api/v1/posts",
            json={
                "scope": "city",
                "city_code": "TPE",
                "category": "trade",
                "title": "Taipei post",
                "content": "Content",
            },
        )

        authenticated_client.post(
            "/api/v1/posts",
            json={
                "scope": "city",
                "city_code": "KHH",
                "category": "trade",
                "title": "Kaohsiung post",
                "content": "Content",
            },
        )

        # List with city_code=TPE
        response = authenticated_client.get("/api/v1/posts?city_code=TPE")

        assert response.status_code == 200
        data = response.json()["data"]

        # Should only include TPE posts
        for post in data["posts"]:
            assert post["city_code"] == "TPE"
            assert post["scope"] == "city"

    def test_category_filtering(self, authenticated_client):
        """Test filtering by category (FR-002)"""
        # Create posts with different categories
        authenticated_client.post(
            "/api/v1/posts",
            json={
                "scope": "global",
                "category": "trade",
                "title": "Trade post",
                "content": "Content",
            },
        )

        authenticated_client.post(
            "/api/v1/posts",
            json={
                "scope": "global",
                "category": "giveaway",
                "title": "Giveaway post",
                "content": "Content",
            },
        )

        # Filter by category=trade
        response = authenticated_client.get("/api/v1/posts?category=trade")

        assert response.status_code == 200
        data = response.json()["data"]

        # Should only include trade posts
        for post in data["posts"]:
            assert post["category"] == "trade"

    def test_list_posts_requires_authentication(self):
        """Test that listing posts requires login (FR-001)"""
        client = TestClient(app)
        response = client.get("/api/v1/posts")

        assert response.status_code == 401

    def test_create_post_requires_authentication(self):
        """Test that creating posts requires login (FR-001)"""
        client = TestClient(app)
        payload = {
            "scope": "global",
            "category": "trade",
            "title": "Test",
            "content": "Test content",
        }

        response = client.post("/api/v1/posts", json=payload)

        assert response.status_code == 401

    @pytest_asyncio.fixture
    async def premium_subscription(self, test_user, db_session) -> None:
        """Ensure the test user has a premium subscription to avoid post quota limits."""
        now = datetime.datetime.utcnow()
        await db_session.execute(
            text(
                """
                INSERT INTO subscriptions (user_id, plan, status, expires_at, created_at, updated_at)
                VALUES (:user_id, :plan, :status, :expires_at, :created_at, :updated_at)
                ON CONFLICT (user_id) DO UPDATE
                SET plan = EXCLUDED.plan,
                    status = EXCLUDED.status,
                    expires_at = EXCLUDED.expires_at,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "user_id": str(test_user),
                "plan": "premium",
                "status": "active",
                "expires_at": datetime.datetime.utcnow() + datetime.timedelta(days=30),
                "created_at": now,
                "updated_at": now,
            },
        )
        await db_session.commit()

    def test_all_categories_are_valid(self, authenticated_client, premium_subscription):
        """Test that all defined categories are accepted (FR-002)"""
        categories = ["trade", "giveaway", "group", "showcase", "help", "announcement"]

        for category in categories:
            payload = {
                "scope": "global",
                "category": category,
                "title": f"Test {category}",
                "content": "Test content",
            }

            response = authenticated_client.post("/api/v1/posts", json=payload)

            assert response.status_code == 201
            data = response.json()["data"]
            assert data["category"] == category
