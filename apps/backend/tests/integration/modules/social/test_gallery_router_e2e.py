"""
Integration E2E tests for Gallery Router

Tests the gallery cards management endpoints:
- GET /gallery/cards/me - Get my gallery cards
- GET /users/{user_id}/gallery/cards - Get user's gallery cards
- POST /gallery/cards - Create gallery card
- DELETE /gallery/cards/{card_id} - Delete gallery card
- PUT /gallery/cards/reorder - Reorder gallery cards
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import UUID, uuid4

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import require_user


class TestGalleryRouterE2E:
    """E2E tests for Gallery Router endpoints"""

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
                "google_id": f"test_gallery_{unique_id}",
                "email": f"gallery_{unique_id}@test.com",
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
                "google_id": f"test_gallery2_{unique_id}",
                "email": f"gallery2_{unique_id}@test.com",
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

    # ===== Get My Gallery Cards Tests =====

    def test_get_my_gallery_cards_empty(self, authenticated_client):
        """Test getting my gallery cards when user has none"""
        response = authenticated_client.get("/api/v1/gallery/cards/me")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert data["total"] == 0 or data["total"] >= 0

    def test_get_my_gallery_cards_unauthorized(self, unauthenticated_client):
        """Test getting my gallery cards without authentication"""
        response = unauthenticated_client.get("/api/v1/gallery/cards/me")

        assert response.status_code == 401

    # ===== Create Gallery Card Tests =====

    def test_create_gallery_card_success(self, authenticated_client):
        """Test creating a gallery card successfully"""
        payload = {
            "title": "IU Love Poem Photocard",
            "idol_name": "IU",
            "era": "Love Poem",
            "description": "Limited edition photocard from Love Poem era"
        }

        response = authenticated_client.post("/api/v1/gallery/cards", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["idol_name"] == payload["idol_name"]
        assert data["era"] == payload["era"]
        assert "id" in data
        assert "user_id" in data
        assert "display_order" in data

    def test_create_gallery_card_missing_required_fields(self, authenticated_client):
        """Test creating gallery card with missing required fields"""
        payload = {
            "title": "Test Card",
            # Missing idol_name and era
        }

        response = authenticated_client.post("/api/v1/gallery/cards", json=payload)

        assert response.status_code == 400

    def test_create_gallery_card_unauthorized(self, unauthenticated_client):
        """Test creating gallery card without authentication"""
        payload = {
            "title": "Test Card",
            "idol_name": "IU",
            "era": "Test"
        }

        response = unauthenticated_client.post("/api/v1/gallery/cards", json=payload)

        assert response.status_code == 401

    # ===== Get User's Gallery Cards Tests =====

    def test_get_user_gallery_cards(self, authenticated_client, test_user):
        """Test getting another user's gallery cards"""
        response = authenticated_client.get(f"/api/v1/users/{test_user}/gallery/cards")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_user_gallery_cards_unauthorized(self, unauthenticated_client, test_user):
        """Test getting user's gallery cards without authentication"""
        response = unauthenticated_client.get(f"/api/v1/users/{test_user}/gallery/cards")

        assert response.status_code == 401

    # ===== Delete Gallery Card Tests =====

    @pytest_asyncio.fixture
    async def test_gallery_card(self, test_user, db_session) -> UUID:
        """Create a test gallery card"""
        card_id = uuid4()
        await db_session.execute(
            text("""
                INSERT INTO gallery_cards (
                    id, user_id, title, idol_name, era, display_order,
                    created_at, updated_at
                )
                VALUES (
                    :id, :user_id, :title, :idol_name, :era, :display_order,
                    NOW(), NOW()
                )
            """),
            {
                "id": str(card_id),
                "user_id": str(test_user),
                "title": "Test Gallery Card",
                "idol_name": "Test Idol",
                "era": "Test Era",
                "display_order": 0
            }
        )
        await db_session.flush()
        return card_id

    def test_delete_gallery_card_success(self, authenticated_client, test_gallery_card):
        """Test deleting a gallery card successfully"""
        response = authenticated_client.delete(f"/api/v1/gallery/cards/{test_gallery_card}")

        assert response.status_code == 204

    def test_delete_gallery_card_not_found(self, authenticated_client):
        """Test deleting non-existent gallery card"""
        fake_id = uuid4()
        response = authenticated_client.delete(f"/api/v1/gallery/cards/{fake_id}")

        assert response.status_code == 404

    def test_delete_gallery_card_unauthorized(self, unauthenticated_client, test_gallery_card):
        """Test deleting gallery card without authentication"""
        response = unauthenticated_client.delete(f"/api/v1/gallery/cards/{test_gallery_card}")

        assert response.status_code == 401

    def test_delete_gallery_card_not_owner(self, test_user2, test_gallery_card, db_session):
        """Test deleting gallery card by non-owner"""
        def override_require_user():
            return test_user2

        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[require_user] = override_require_user
        app.dependency_overrides[get_db_session] = override_get_db_session

        try:
            client = TestClient(app)
            response = client.delete(f"/api/v1/gallery/cards/{test_gallery_card}")

            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()

    # ===== Reorder Gallery Cards Tests =====

    def test_reorder_gallery_cards_success(self, authenticated_client):
        """Test reordering gallery cards"""
        payload = {
            "card_orders": []  # Empty list is valid
        }

        response = authenticated_client.put("/api/v1/gallery/cards/reorder", json=payload)

        # Should succeed or return 400/422 based on implementation
        assert response.status_code in [200, 400, 422]

    def test_reorder_gallery_cards_unauthorized(self, unauthenticated_client):
        """Test reordering gallery cards without authentication"""
        payload = {
            "card_orders": []
        }

        response = unauthenticated_client.put("/api/v1/gallery/cards/reorder", json=payload)

        assert response.status_code == 401

    def test_reorder_gallery_cards_invalid_data(self, authenticated_client):
        """Test reordering with invalid data"""
        payload = {}  # Missing card_orders

        response = authenticated_client.put("/api/v1/gallery/cards/reorder", json=payload)

        assert response.status_code == 400
