"""
Integration E2E tests for Cards Router

Tests the cards management endpoints:
- POST /cards/upload-url - Generate upload URL
- GET /cards/me - Get my cards
- DELETE /cards/{card_id} - Delete card
- POST /cards/{card_id}/confirm-upload - Confirm upload
- GET /cards/quota/status - Get quota status
"""

from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id


class TestCardsRouterE2E:
    """E2E tests for Cards Router endpoints"""

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
                "google_id": f"test_cards_{unique_id}",
                "email": f"cards_{unique_id}@test.com",
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

    @pytest.fixture
    def unauthenticated_client(self, app_db_session_override):
        """Provide unauthenticated test client"""
        app.dependency_overrides[get_db_session] = app_db_session_override

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    def test_get_my_cards_empty(self, authenticated_client):
        """Test getting my cards when user has no cards"""
        response = authenticated_client.get("/api/v1/cards/me")

        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_my_cards_unauthorized(self, unauthenticated_client):
        """Test getting cards without authentication"""
        response = unauthenticated_client.get("/api/v1/cards/me")

        assert response.status_code == 401

    def test_upload_url_success(self, authenticated_client):
        """Test generating upload URL successfully"""
        payload = {
            "content_type": "image/jpeg",
            "file_size_bytes": 1024000,  # 1MB
            "idol": "Jungkook",
            "idol_group": "BTS",
            "album": "BE",
            "version": "Deluxe",
            "rarity": "rare",
        }

        response = authenticated_client.post("/api/v1/cards/upload-url", json=payload)

        # Should succeed or fail based on GCS configuration
        assert response.status_code in [200, 422]

        if response.status_code == 200:
            data = response.json()["data"]
            assert "upload_url" in data
            assert "card_id" in data
            assert "image_url" in data
            assert "method" in data
            assert "expires_at" in data

    def test_upload_url_invalid_content_type(self, authenticated_client):
        """Test upload URL with invalid content type"""
        payload = {
            "content_type": "text/plain",  # Invalid
            "file_size_bytes": 1024000,
            "idol": "Jungkook",
            "idol_group": "BTS",
            "album": "BE",
            "version": "Deluxe",
            "rarity": "rare",
        }

        response = authenticated_client.post("/api/v1/cards/upload-url", json=payload)

        assert response.status_code == 400

    def test_upload_url_file_too_large(self, authenticated_client):
        """Test upload URL with file size exceeding limit"""
        payload = {
            "content_type": "image/jpeg",
            "file_size_bytes": 50 * 1024 * 1024,  # 50MB (should exceed limit)
            "idol": "Jungkook",
            "idol_group": "BTS",
            "album": "BE",
            "version": "Deluxe",
            "rarity": "rare",
        }

        response = authenticated_client.post("/api/v1/cards/upload-url", json=payload)

        assert response.status_code in [400, 422]

    def test_upload_url_missing_fields(self, authenticated_client):
        """Test upload URL with missing required fields"""
        payload = {
            "content_type": "image/jpeg",
            # Missing file_size_bytes and other required fields
        }

        response = authenticated_client.post("/api/v1/cards/upload-url", json=payload)

        assert response.status_code == 400

    def test_upload_url_unauthorized(self, unauthenticated_client):
        """Test upload URL without authentication"""
        payload = {
            "content_type": "image/jpeg",
            "file_size_bytes": 1024000,
            "idol": "Jungkook",
            "idol_group": "BTS",
            "album": "BE",
            "version": "Deluxe",
            "rarity": "rare",
        }

        response = unauthenticated_client.post("/api/v1/cards/upload-url", json=payload)

        assert response.status_code == 401

    def test_get_quota_status(self, authenticated_client):
        """Test getting quota status"""
        response = authenticated_client.get("/api/v1/cards/quota/status")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "uploads_today" in data
        assert "daily_limit" in data
        assert "storage_used_bytes" in data
        assert "storage_limit_bytes" in data

    def test_get_quota_status_unauthorized(self, unauthenticated_client):
        """Test quota status without authentication"""
        response = unauthenticated_client.get("/api/v1/cards/quota/status")

        assert response.status_code == 401

    @pytest_asyncio.fixture
    async def test_card(self, test_user, db_session) -> UUID:
        """Create a test card for the user"""
        card_id = uuid4()
        await db_session.execute(
            text(
                """
                INSERT INTO cards (
                    id, owner_id, idol, idol_group, album, version, rarity,
                    status, image_url, size_bytes
                )
                VALUES (
                    :id, :owner_id, :idol, :idol_group, :album, :version, :rarity,
                    :status, :image_url, :size_bytes
                )
            """
            ),
            {
                "id": str(card_id),
                "owner_id": str(test_user),
                "idol": "Test Idol",
                "idol_group": "Test Group",
                "album": "Test Album",
                "version": "Standard",
                "rarity": "common",
                "status": "available",
                "image_url": "https://example.com/card.jpg",
                "size_bytes": 1024000,
            },
        )
        await db_session.commit()
        return card_id

    def test_get_my_cards_with_cards(self, authenticated_client, test_card):
        """Test getting my cards when user has cards"""
        response = authenticated_client.get("/api/v1/cards/me")

        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, list)
        assert len(data) > 0

        card = data[0]
        assert "id" in card
        assert "idol" in card
        assert "idol_group" in card
        assert "album" in card
        assert "status" in card

    def test_delete_card_success(self, authenticated_client, test_card):
        """Test deleting a card successfully"""
        response = authenticated_client.delete(f"/api/v1/cards/{test_card}")

        # Should succeed or return not found if GCS deletion fails
        assert response.status_code in [200, 404]

    def test_delete_card_not_found(self, authenticated_client):
        """Test deleting non-existent card"""
        fake_id = uuid4()
        response = authenticated_client.delete(f"/api/v1/cards/{fake_id}")

        assert response.status_code == 404

    def test_delete_card_unauthorized(self, unauthenticated_client, test_card):
        """Test deleting card without authentication"""
        response = unauthenticated_client.delete(f"/api/v1/cards/{test_card}")

        assert response.status_code == 401

    def test_confirm_upload_card_not_found(self, authenticated_client):
        """Test confirming upload for non-existent card"""
        fake_id = uuid4()
        response = authenticated_client.post(f"/api/v1/cards/{fake_id}/confirm-upload")

        assert response.status_code == 404

    def test_confirm_upload_unauthorized(self, unauthenticated_client, test_card):
        """Test confirming upload without authentication"""
        response = unauthenticated_client.post(
            f"/api/v1/cards/{test_card}/confirm-upload"
        )

        assert response.status_code == 401
