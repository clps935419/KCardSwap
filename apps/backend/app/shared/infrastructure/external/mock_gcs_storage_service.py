"""Mock Google Cloud Storage service for development and testing.

This module provides a mock implementation of GCS for local development
and testing environments, avoiding the need to connect to real GCS.
"""

from datetime import datetime
from typing import Optional


class MockGCSStorageService:
    """Mock implementation of GCS storage service.

    This service mimics the behavior of GCSStorageService without actually
    connecting to Google Cloud Storage. It's used for:
    - Local development (when USE_MOCK_GCS=true)
    - Unit tests (always mocked)
    - Integration tests (always mocked)

    Real GCS is only used for Staging/Nightly smoke tests when RUN_GCS_SMOKE=1.
    """

    def __init__(
        self,
        bucket_name: str = "kcardswap-mock",
        credentials_path: Optional[str] = None,
    ) -> None:
        """Initialize mock GCS storage service.

        Args:
            bucket_name: Name of the mock GCS bucket (ignored)
            credentials_path: Path to credentials (ignored)
        """
        self._bucket_name = bucket_name
        self._credentials_path = credentials_path
        self._mock_storage = {}  # In-memory storage for blob metadata

    def _ensure_initialized(self) -> None:
        """Mock initialization - no-op for mock service."""
        pass

    def generate_upload_signed_url(
        self,
        blob_name: str,
        content_type: str = "image/jpeg",
        expiration_minutes: int = 15,
    ) -> str:
        """Generate a mock signed URL for uploading a file.

        Args:
            blob_name: Name/path of the blob in GCS (e.g., 'cards/user_id/card_id.jpg')
            content_type: MIME type of the file
            expiration_minutes: URL expiration time in minutes

        Returns:
            Mock signed URL for uploading
        """
        # Validate blob_name follows the correct pattern
        if not (blob_name.startswith("cards/") or blob_name.startswith("media/")):
            raise ValueError(
                f"Invalid blob path: {blob_name}. Must start with 'cards/' or 'media/'"
            )

        if "thumbs" in blob_name.lower():
            raise ValueError(
                f"Invalid blob path: {blob_name}. 'thumbs/' is not allowed"
            )

        # Return a mock URL that looks realistic but won't actually work
        base_url = f"https://storage.googleapis.com/{self._bucket_name}/{blob_name}"
        # Mock signature format: expiration_minutes is multiplied by 100 for the Expires parameter
        # This mimics GCS URL format where Expires is in seconds (e.g., 15 min * 60 sec/min = 900, then * 100 for mock)
        mock_signature = "X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mock&X-Goog-Date=mock&X-Goog-Expires={expiration_minutes}00&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=mock_signature"

        return f"{base_url}?{mock_signature}"

    def generate_download_signed_url(
        self, blob_name: str, expiration_minutes: int = 60
    ) -> str:
        """Generate a mock signed URL for downloading a file.

        Args:
            blob_name: Name/path of the blob in GCS
            expiration_minutes: URL expiration time in minutes

        Returns:
            Mock signed URL for downloading
        """
        # Validate blob_name follows the correct pattern
        if not (blob_name.startswith("cards/") or blob_name.startswith("media/")):
            raise ValueError(
                f"Invalid blob path: {blob_name}. Must start with 'cards/' or 'media/'"
            )

        base_url = f"https://storage.googleapis.com/{self._bucket_name}/{blob_name}"
        mock_signature = f"X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mock&X-Goog-Date=mock&X-Goog-Expires={expiration_minutes}00&X-Goog-SignedHeaders=host&X-Goog-Signature=mock_signature"

        return f"{base_url}?{mock_signature}"

    def delete_blob(self, blob_name: str) -> bool:
        """Mock delete a blob from GCS.

        Args:
            blob_name: Name/path of the blob to delete

        Returns:
            True if blob was deleted, False if not found
        """
        if blob_name in self._mock_storage:
            del self._mock_storage[blob_name]
            return True
        return False

    def blob_exists(self, blob_name: str) -> bool:
        """Mock check if a blob exists in GCS.

        Args:
            blob_name: Name/path of the blob

        Returns:
            True if blob exists in mock storage, False otherwise
        """
        return blob_name in self._mock_storage

    def get_blob_metadata(self, blob_name: str) -> Optional[dict]:
        """Get mock metadata for a blob.

        Args:
            blob_name: Name/path of the blob

        Returns:
            Mock metadata dictionary if blob exists, None otherwise
        """
        if blob_name not in self._mock_storage:
            return None

        # Return mock metadata
        return {
            "name": blob_name,
            "size": 100 * 1024,  # 100 KB default mock file size
            "content_type": "image/jpeg",
            "created": datetime.utcnow(),
            "updated": datetime.utcnow(),
        }

    def _add_mock_blob(self, blob_name: str, size: int = 100 * 1024) -> None:
        """Helper method to add a mock blob to storage (for testing).

        Args:
            blob_name: Name/path of the blob
            size: Size of the blob in bytes (default: 100 KB)
        """
        self._mock_storage[blob_name] = {
            "name": blob_name,
            "size": size,
            "content_type": "image/jpeg",
            "created": datetime.utcnow(),
            "updated": datetime.utcnow(),
        }


# Global mock GCS storage service instance
mock_gcs_storage_service = MockGCSStorageService()
