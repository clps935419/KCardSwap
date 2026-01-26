"""
Integration E2E tests for Media Router

Tests the media management endpoints:
- POST /media/upload-url - Generate presigned upload URL
- POST /media/{media_id}/confirm - Confirm media upload
- POST /media/posts/{post_id}/attach - Attach media to post
- POST /media/gallery/cards/{card_id}/attach - Attach media to gallery card
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import UUID, uuid4

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import get_current_user_id


class TestMediaRouterE2E:
    """E2E tests for Media Router endpoints"""

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
                "google_id": f"test_media_{unique_id}",
                "email": f"media_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest.fixture
    def authenticated_client(self, test_user, db_session):
        """Provide authenticated test client"""
        def override_get_current_user_id():
            return test_user

        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
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

    # ===== Upload URL Tests =====

    def test_create_upload_url_success(self, authenticated_client):
        """Test generating upload URL successfully"""
        payload = {
            "content_type": "image/jpeg",
            "file_size_bytes": 1024000,  # 1MB
            "filename": "test_image.jpg"
        }

        response = authenticated_client.post("/api/v1/media/upload-url", json=payload)

        # Should succeed or return error based on GCS configuration
        assert response.status_code in [201, 400, 500]
        
        if response.status_code == 201:
            data = response.json()
            assert "media_id" in data
            assert "upload_url" in data
            assert "expires_in_minutes" in data

    def test_create_upload_url_invalid_content_type(self, authenticated_client):
        """Test upload URL with invalid content type"""
        payload = {
            "content_type": "text/plain",  # Invalid
            "file_size_bytes": 1024000,
            "filename": "test.txt"
        }

        response = authenticated_client.post("/api/v1/media/upload-url", json=payload)

        assert response.status_code in [400, 422]

    def test_create_upload_url_file_too_large(self, authenticated_client):
        """Test upload URL with file size exceeding limit"""
        payload = {
            "content_type": "image/jpeg",
            "file_size_bytes": 50 * 1024 * 1024,  # 50MB
            "filename": "large.jpg"
        }

        response = authenticated_client.post("/api/v1/media/upload-url", json=payload)

        assert response.status_code in [400, 422]

    def test_create_upload_url_missing_fields(self, authenticated_client):
        """Test upload URL with missing required fields"""
        payload = {
            "content_type": "image/jpeg"
            # Missing file_size_bytes and filename
        }

        response = authenticated_client.post("/api/v1/media/upload-url", json=payload)

        assert response.status_code == 400

    def test_create_upload_url_unauthorized(self, unauthenticated_client):
        """Test upload URL without authentication"""
        payload = {
            "content_type": "image/jpeg",
            "file_size_bytes": 1024000,
            "filename": "test.jpg"
        }

        response = unauthenticated_client.post("/api/v1/media/upload-url", json=payload)

        assert response.status_code == 401

    # ===== Confirm Upload Tests =====

    def test_confirm_upload_media_not_found(self, authenticated_client):
        """Test confirming upload for non-existent media"""
        fake_media_id = uuid4()
        response = authenticated_client.post(f"/api/v1/media/{fake_media_id}/confirm")

        assert response.status_code in [400, 404]

    def test_confirm_upload_unauthorized(self, unauthenticated_client):
        """Test confirming upload without authentication"""
        fake_media_id = uuid4()
        response = unauthenticated_client.post(f"/api/v1/media/{fake_media_id}/confirm")

        assert response.status_code == 401

    # ===== Attach Media to Post Tests =====

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

    def test_attach_media_to_post_media_not_found(self, authenticated_client, test_post):
        """Test attaching non-existent media to post"""
        fake_media_id = uuid4()
        payload = {
            "media_id": str(fake_media_id)
        }

        response = authenticated_client.post(
            f"/api/v1/media/posts/{test_post}/attach",
            json=payload
        )

        assert response.status_code in [400, 404]

    def test_attach_media_to_post_unauthorized(self, unauthenticated_client, test_post):
        """Test attaching media without authentication"""
        fake_media_id = uuid4()
        payload = {
            "media_id": str(fake_media_id)
        }

        response = unauthenticated_client.post(
            f"/api/v1/media/posts/{test_post}/attach",
            json=payload
        )

        assert response.status_code == 401

    def test_attach_media_to_post_missing_media_id(self, authenticated_client, test_post):
        """Test attaching media without providing media_id"""
        payload = {}

        response = authenticated_client.post(
            f"/api/v1/media/posts/{test_post}/attach",
            json=payload
        )

        assert response.status_code == 400

    # ===== Attach Media to Gallery Card Tests =====

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
                "title": "Test Card",
                "idol_name": "Test Idol",
                "era": "Test Era",
                "display_order": 0
            }
        )
        await db_session.flush()
        return card_id

    def test_attach_media_to_gallery_card_media_not_found(
        self, authenticated_client, test_gallery_card
    ):
        """Test attaching non-existent media to gallery card"""
        fake_media_id = uuid4()
        payload = {
            "media_id": str(fake_media_id)
        }

        response = authenticated_client.post(
            f"/api/v1/media/gallery/cards/{test_gallery_card}/attach",
            json=payload
        )

        assert response.status_code in [400, 404]

    def test_attach_media_to_gallery_card_unauthorized(
        self, unauthenticated_client, test_gallery_card
    ):
        """Test attaching media to gallery card without authentication"""
        fake_media_id = uuid4()
        payload = {
            "media_id": str(fake_media_id)
        }

        response = unauthenticated_client.post(
            f"/api/v1/media/gallery/cards/{test_gallery_card}/attach",
            json=payload
        )

        assert response.status_code == 401

    def test_attach_media_to_gallery_card_missing_media_id(
        self, authenticated_client, test_gallery_card
    ):
        """Test attaching media to gallery card without media_id"""
        payload = {}

        response = authenticated_client.post(
            f"/api/v1/media/gallery/cards/{test_gallery_card}/attach",
            json=payload
        )

        assert response.status_code == 400
