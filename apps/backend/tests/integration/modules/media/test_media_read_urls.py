"""
Integration tests for Media Read URLs (Phase 9)

Tests the media read URL endpoint:
- POST /media/read-urls - Batch retrieve signed read URLs for media assets
"""

from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import get_current_user_id


class TestMediaReadUrls:
    """Integration tests for media read URLs (Phase 9)"""

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
                "google_id": f"test_read_urls_{unique_id}",
                "email": f"read_urls_{unique_id}@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.commit()
        return user_id

    @pytest_asyncio.fixture
    async def confirmed_media(self, db_session, test_user) -> UUID:
        """Create a confirmed media asset for testing"""
        media_id = str(uuid4())
        await db_session.execute(
            text(
                """
                INSERT INTO media_assets 
                (id, owner_id, gcs_blob_name, content_type, file_size_bytes, status, confirmed_at)
                VALUES (:id, :owner_id, :blob_name, :content_type, :file_size, :status, NOW())
            """
            ),
            {
                "id": media_id,
                "owner_id": str(test_user),
                "blob_name": f"test/media/{media_id}.jpg",
                "content_type": "image/jpeg",
                "file_size": 1024000,
                "status": "confirmed",
            },
        )
        await db_session.commit()
        return UUID(media_id)

    @pytest_asyncio.fixture
    async def attached_media(self, db_session, test_user) -> UUID:
        """Create an attached media asset for testing"""
        media_id = str(uuid4())
        post_id = str(uuid4())
        
        # Create a post first
        await db_session.execute(
            text(
                """
                INSERT INTO posts 
                (id, owner_id, scope, category, title, content, status, expires_at)
                VALUES (:id, :owner_id, 'global', 'showcase', 'Test Post', 'Test', 'open', NOW() + INTERVAL '14 days')
            """
            ),
            {"id": post_id, "owner_id": str(test_user)},
        )
        
        # Create attached media
        await db_session.execute(
            text(
                """
                INSERT INTO media_assets 
                (id, owner_id, gcs_blob_name, content_type, file_size_bytes, status, confirmed_at, target_type, target_id)
                VALUES (:id, :owner_id, :blob_name, :content_type, :file_size, :status, NOW(), :target_type, :target_id)
            """
            ),
            {
                "id": media_id,
                "owner_id": str(test_user),
                "blob_name": f"test/media/{media_id}.jpg",
                "content_type": "image/jpeg",
                "file_size": 1024000,
                "status": "attached",
                "target_type": "post",
                "target_id": post_id,
            },
        )
        await db_session.commit()
        return UUID(media_id)

    @pytest.fixture
    def authenticated_client(self, test_user, app_db_session_override):
        """Provide authenticated test client"""

        def override_get_current_user_id():
            return test_user

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = app_db_session_override

        with TestClient(app) as client:
            yield client

        app.dependency_overrides.clear()

    def test_read_urls_success_confirmed_media(
        self, authenticated_client, confirmed_media
    ):
        """Test successful batch retrieval of signed read URLs for confirmed media"""
        # Arrange
        media_ids = [str(confirmed_media)]

        # Act
        response = authenticated_client.post(
            "/api/v1/media/read-urls",
            json={"media_asset_ids": media_ids},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "urls" in data["data"]
        assert "expires_in_minutes" in data["data"]
        
        # Check URLs were generated
        urls = data["data"]["urls"]
        assert str(confirmed_media) in urls
        assert urls[str(confirmed_media)].startswith("https://")
        
        # Check TTL
        assert data["data"]["expires_in_minutes"] == 10

    def test_read_urls_success_attached_media(
        self, authenticated_client, attached_media
    ):
        """Test successful retrieval of URLs for attached media"""
        # Arrange
        media_ids = [str(attached_media)]

        # Act
        response = authenticated_client.post(
            "/api/v1/media/read-urls",
            json={"media_asset_ids": media_ids},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        urls = data["data"]["urls"]
        assert str(attached_media) in urls

    def test_read_urls_multiple_media(
        self, authenticated_client, confirmed_media, attached_media
    ):
        """Test batch retrieval of multiple media assets"""
        # Arrange
        media_ids = [str(confirmed_media), str(attached_media)]

        # Act
        response = authenticated_client.post(
            "/api/v1/media/read-urls",
            json={"media_asset_ids": media_ids},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        urls = data["data"]["urls"]
        
        # Both media should have URLs
        assert str(confirmed_media) in urls
        assert str(attached_media) in urls

    def test_read_urls_empty_list(self, authenticated_client):
        """Test with empty media asset list"""
        # Arrange
        media_ids = []

        # Act
        response = authenticated_client.post(
            "/api/v1/media/read-urls",
            json={"media_asset_ids": media_ids},
        )

        # Assert - Should fail validation (min_length=1)
        assert response.status_code == 422

    def test_read_urls_nonexistent_media(self, authenticated_client):
        """Test with non-existent media IDs"""
        # Arrange
        fake_media_id = str(uuid4())

        # Act
        response = authenticated_client.post(
            "/api/v1/media/read-urls",
            json={"media_asset_ids": [fake_media_id]},
        )

        # Assert - Should succeed but return empty urls
        assert response.status_code == 200
        data = response.json()
        urls = data["data"]["urls"]
        assert fake_media_id not in urls

    def test_read_urls_requires_authentication(self):
        """Test that read URLs endpoint requires authentication"""
        # Arrange
        client = TestClient(app)
        media_ids = [str(uuid4())]

        # Act
        response = client.post(
            "/api/v1/media/read-urls",
            json={"media_asset_ids": media_ids},
        )

        # Assert - Should fail with 401 (unauthorized)
        assert response.status_code == 401

    @pytest_asyncio.fixture
    async def pending_media(self, db_session, test_user) -> UUID:
        """Create a pending media asset (should not be accessible)"""
        media_id = str(uuid4())
        await db_session.execute(
            text(
                """
                INSERT INTO media_assets 
                (id, owner_id, gcs_blob_name, content_type, file_size_bytes, status)
                VALUES (:id, :owner_id, :blob_name, :content_type, :file_size, :status)
            """
            ),
            {
                "id": media_id,
                "owner_id": str(test_user),
                "blob_name": f"test/media/{media_id}.jpg",
                "content_type": "image/jpeg",
                "file_size": 1024000,
                "status": "pending",
            },
        )
        await db_session.commit()
        return UUID(media_id)

    def test_read_urls_filters_pending_media(
        self, authenticated_client, pending_media, confirmed_media
    ):
        """Test that pending media is filtered out and only confirmed/attached are returned"""
        # Arrange
        media_ids = [str(pending_media), str(confirmed_media)]

        # Act
        response = authenticated_client.post(
            "/api/v1/media/read-urls",
            json={"media_asset_ids": media_ids},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        urls = data["data"]["urls"]
        
        # Pending media should NOT have URL
        assert str(pending_media) not in urls
        
        # Confirmed media should have URL
        assert str(confirmed_media) in urls
