"""
Unit tests for MockGCSStorageService

Tests the mock GCS storage service used for development and testing.
"""

import pytest

from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)


class TestMockGCSStorageService:
    """Test MockGCSStorageService"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return MockGCSStorageService(bucket_name="test-bucket")

    def test_init(self):
        """Test service initialization"""
        # Act
        service = MockGCSStorageService(
            bucket_name="my-bucket", credentials_path="/path/to/creds"
        )

        # Assert
        assert service._bucket_name == "my-bucket"
        assert service._credentials_path == "/path/to/creds"

    def test_init_default_bucket(self):
        """Test service initialization with default bucket"""
        # Act
        service = MockGCSStorageService()

        # Assert
        assert service._bucket_name == "kcardswap-mock"

    def test_generate_upload_signed_url_valid(self, service):
        """Test generating upload signed URL with valid blob name"""
        # Act
        url = service.generate_upload_signed_url(
            blob_name="cards/user123/card456.jpg",
            content_type="image/jpeg",
            expiration_minutes=15,
        )

        # Assert
        assert "storage.googleapis.com" in url
        assert "test-bucket" in url
        assert "cards/user123/card456.jpg" in url
        assert "X-Goog-Algorithm" in url

    def test_generate_upload_signed_url_invalid_prefix(self, service):
        """Test that upload URL generation rejects invalid blob prefix"""
        # Act & Assert
        with pytest.raises(ValueError, match="Must start with 'cards/'"):
            service.generate_upload_signed_url(blob_name="invalid/path.jpg")

    def test_generate_upload_signed_url_rejects_thumbs(self, service):
        """Test that upload URL generation rejects thumbs directory"""
        # Act & Assert
        with pytest.raises(ValueError, match="'thumbs/' is not allowed"):
            service.generate_upload_signed_url(blob_name="cards/user/thumbs/img.jpg")

    def test_generate_upload_signed_url_with_png(self, service):
        """Test generating upload signed URL with PNG content type"""
        # Act
        url = service.generate_upload_signed_url(
            blob_name="cards/user123/card456.png",
            content_type="image/png",
            expiration_minutes=30,
        )

        # Assert
        assert "storage.googleapis.com" in url
        assert "cards/user123/card456.png" in url

    def test_generate_download_signed_url_valid(self, service):
        """Test generating download signed URL with valid blob name"""
        # Act
        url = service.generate_download_signed_url(
            blob_name="cards/user123/card456.jpg", expiration_minutes=60
        )

        # Assert
        assert "storage.googleapis.com" in url
        assert "test-bucket" in url
        assert "cards/user123/card456.jpg" in url
        assert "X-Goog-Algorithm" in url

    def test_generate_download_signed_url_invalid_prefix(self, service):
        """Test that download URL generation rejects invalid blob prefix"""
        # Act & Assert
        with pytest.raises(ValueError, match="Must start with 'cards/'"):
            service.generate_download_signed_url(blob_name="bad/path.jpg")

    def test_delete_blob(self, service):
        """Test deleting a blob"""
        # Arrange - Add a blob first
        service._add_mock_blob("cards/user123/card456.jpg")
        
        # Act
        result = service.delete_blob(blob_name="cards/user123/card456.jpg")

        # Assert
        assert result is True

    def test_blob_exists_returns_true(self, service):
        """Test blob_exists returns True for existing blob"""
        # Arrange
        service._add_mock_blob("cards/user123/card456.jpg")
        
        # Act
        exists = service.blob_exists(blob_name="cards/user123/card456.jpg")

        # Assert
        assert exists is True

    def test_blob_exists_returns_false(self, service):
        """Test blob_exists returns False for non-existing blob"""
        # Act
        exists = service.blob_exists(blob_name="cards/any/path/file.jpg")

        # Assert
        assert exists is False

    def test_ensure_initialized_no_op(self, service):
        """Test that _ensure_initialized is a no-op"""
        # Act & Assert - should not raise
        service._ensure_initialized()

    def test_bucket_name_property(self, service):
        """Test _bucket_name property"""
        # Assert
        assert service._bucket_name == "test-bucket"

    def test_credentials_path_property(self, service):
        """Test _credentials_path property"""
        # Arrange
        service = MockGCSStorageService(
            bucket_name="test-bucket", credentials_path="/custom/path"
        )

        # Assert
        assert service._credentials_path == "/custom/path"

    def test_url_format_is_valid(self, service):
        """Test that generated URLs follow expected format"""
        # Act
        url = service.generate_upload_signed_url(
            blob_name="cards/user/file.jpg", expiration_minutes=20
        )

        # Assert - Check URL contains expected components
        assert url.startswith("https://storage.googleapis.com/")
        assert "cards/user/file.jpg" in url
        assert "X-Goog-Algorithm" in url

    def test_multiple_url_generations(self, service):
        """Test generating multiple URLs works correctly"""
        # Act
        url1 = service.generate_upload_signed_url(blob_name="cards/user1/file1.jpg")
        url2 = service.generate_upload_signed_url(blob_name="cards/user2/file2.jpg")
        url3 = service.generate_download_signed_url(blob_name="cards/user3/file3.jpg")

        # Assert
        assert "file1.jpg" in url1
        assert "file2.jpg" in url2
        assert "file3.jpg" in url3
        assert url1 != url2
        assert url2 != url3
