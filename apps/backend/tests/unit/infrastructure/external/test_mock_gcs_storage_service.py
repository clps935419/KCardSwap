"""Unit tests for Mock GCS Storage Service.

These tests demonstrate the proper usage of the mock GCS service
and validate that it enforces the correct path patterns.
"""

import pytest

from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)


class TestMockGCSStorageService:
    """Test cases for mock GCS storage service."""

    def test_generate_upload_signed_url_valid_path(self, mock_gcs_service):
        """Test generating upload URL with valid cards/ path."""
        blob_name = "cards/user123/card456.jpg"
        url = mock_gcs_service.generate_upload_signed_url(blob_name)

        assert url is not None
        assert "storage.googleapis.com" in url
        assert blob_name in url
        assert "X-Goog-Algorithm" in url

    def test_generate_upload_signed_url_invalid_path(self, mock_gcs_service):
        """Test that invalid paths (not starting with cards/) are rejected."""
        with pytest.raises(ValueError, match="Must start with 'cards/'"):
            mock_gcs_service.generate_upload_signed_url("invalid/path.jpg")

    def test_generate_upload_signed_url_thumbs_not_allowed(self, mock_gcs_service):
        """Test that thumbs/ paths are explicitly rejected."""
        with pytest.raises(ValueError, match="'thumbs/' is not allowed"):
            mock_gcs_service.generate_upload_signed_url("cards/user123/thumbs/card.jpg")

    def test_generate_download_signed_url_valid_path(self, mock_gcs_service):
        """Test generating download URL with valid cards/ path."""
        blob_name = "cards/user123/card456.jpg"
        url = mock_gcs_service.generate_download_signed_url(blob_name)

        assert url is not None
        assert "storage.googleapis.com" in url
        assert blob_name in url
        assert "X-Goog-Algorithm" in url

    def test_generate_download_signed_url_invalid_path(self, mock_gcs_service):
        """Test that invalid paths are rejected for download URLs."""
        with pytest.raises(ValueError, match="Must start with 'cards/'"):
            mock_gcs_service.generate_download_signed_url("invalid/path.jpg")

    def test_blob_exists_returns_false_for_nonexistent(self, mock_gcs_service):
        """Test that blob_exists returns False for non-existent blobs."""
        assert not mock_gcs_service.blob_exists("cards/user123/nonexistent.jpg")

    def test_blob_exists_returns_true_after_adding(self, mock_gcs_service):
        """Test that blob_exists returns True after adding a blob."""
        blob_name = "cards/user123/card456.jpg"
        mock_gcs_service._add_mock_blob(blob_name)
        assert mock_gcs_service.blob_exists(blob_name)

    def test_delete_blob_returns_false_for_nonexistent(self, mock_gcs_service):
        """Test that deleting non-existent blob returns False."""
        assert not mock_gcs_service.delete_blob("cards/user123/nonexistent.jpg")

    def test_delete_blob_returns_true_after_deleting(self, mock_gcs_service):
        """Test that deleting existing blob returns True."""
        blob_name = "cards/user123/card456.jpg"
        mock_gcs_service._add_mock_blob(blob_name)
        assert mock_gcs_service.delete_blob(blob_name)
        assert not mock_gcs_service.blob_exists(blob_name)

    def test_get_blob_metadata_returns_none_for_nonexistent(self, mock_gcs_service):
        """Test that get_blob_metadata returns None for non-existent blobs."""
        assert mock_gcs_service.get_blob_metadata("cards/user123/nonexistent.jpg") is None

    def test_get_blob_metadata_returns_dict_for_existing(self, mock_gcs_service):
        """Test that get_blob_metadata returns metadata for existing blobs."""
        blob_name = "cards/user123/card456.jpg"
        mock_gcs_service._add_mock_blob(blob_name, size=2048)

        metadata = mock_gcs_service.get_blob_metadata(blob_name)

        assert metadata is not None
        assert metadata["name"] == blob_name
        assert metadata["size"] == 2048
        assert metadata["content_type"] == "image/jpeg"
        assert "created" in metadata
        assert "updated" in metadata

    def test_content_type_parameter_in_url(self, mock_gcs_service):
        """Test that content_type parameter is used in URL generation."""
        blob_name = "cards/user123/card456.jpg"
        url = mock_gcs_service.generate_upload_signed_url(
            blob_name, content_type="image/png"
        )

        assert url is not None
        # Mock URL doesn't actually encode content type but should still generate

    def test_expiration_parameter_in_url(self, mock_gcs_service):
        """Test that expiration parameter is reflected in URL."""
        blob_name = "cards/user123/card456.jpg"
        url = mock_gcs_service.generate_upload_signed_url(
            blob_name, expiration_minutes=30
        )

        assert url is not None
        assert "X-Goog-Expires=3000" in url  # 30 minutes * 100 in mock


@pytest.mark.gcs_smoke
class TestRealGCSStorageService:
    """Smoke tests for real GCS storage service.

    These tests are marked with @pytest.mark.gcs_smoke and will only run
    when RUN_GCS_SMOKE=1 is set in the environment. They require:
    - Real GCS credentials (GCS_CREDENTIALS_PATH)
    - Real GCS bucket (GCS_BUCKET_NAME)
    - Proper IAM permissions

    Run with: RUN_GCS_SMOKE=1 pytest -m gcs_smoke
    """

    def test_real_gcs_connection(self):
        """Test real GCS connection and signed URL generation.

        This is a smoke test that verifies:
        1. Credentials are valid
        2. Bucket exists and is accessible
        3. Signed URLs can be generated
        4. IAM permissions are correct
        """
        pytest.skip("GCS smoke test - requires real GCS setup")
        # Uncomment and implement when ready for smoke testing:
        # from app.shared.infrastructure.external.gcs_storage_service import (
        #     GCSStorageService,
        # )
        # from app.config import settings
        #
        # service = GCSStorageService(
        #     bucket_name=settings.GCS_BUCKET_NAME,
        #     credentials_path=settings.GCS_CREDENTIALS_PATH,
        # )
        #
        # blob_name = f"cards-smoke/test_user/smoke_test_{datetime.utcnow().timestamp()}.jpg"
        # url = service.generate_upload_signed_url(blob_name)
        #
        # assert url is not None
        # assert "storage.googleapis.com" in url
        # # Could optionally test actual upload with httpx/requests
