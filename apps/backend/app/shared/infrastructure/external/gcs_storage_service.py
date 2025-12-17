"""Google Cloud Storage service for file management.

This module provides GCS integration for generating signed URLs for file uploads.
"""

from datetime import timedelta
from typing import Optional

from google.cloud import storage
from google.oauth2 import service_account

from app.config import settings


class GCSStorageService:
    """Service for Google Cloud Storage operations.

    Handles signed URL generation for secure file uploads to GCS.
    Uses lazy initialization to avoid authentication errors during startup.
    """

    def __init__(
        self,
        bucket_name: str = settings.GCS_BUCKET_NAME,
        credentials_path: Optional[str] = settings.GCS_CREDENTIALS_PATH,
    ) -> None:
        """Initialize GCS storage service (lazy initialization).

        Args:
            bucket_name: Name of the GCS bucket
            credentials_path: Path to service account credentials JSON file
        """
        self._bucket_name = bucket_name
        self._credentials_path = credentials_path
        self._client: Optional[storage.Client] = None
        self._bucket: Optional[storage.Bucket] = None

    def _ensure_initialized(self) -> None:
        """Lazy initialization of GCS client."""
        if self._client is not None:
            return

        if self._credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                self._credentials_path
            )
            self._client = storage.Client(credentials=credentials)
        else:
            # Use default credentials (e.g., from GCE metadata)
            self._client = storage.Client()

        self._bucket = self._client.bucket(self._bucket_name)

    def generate_upload_signed_url(
        self,
        blob_name: str,
        content_type: str = "image/jpeg",
        expiration_minutes: int = 15,
    ) -> str:
        """Generate a signed URL for uploading a file.

        Args:
            blob_name: Name/path of the blob in GCS (e.g., 'cards/user_id/card_id.jpg')
            content_type: MIME type of the file
            expiration_minutes: URL expiration time in minutes

        Returns:
            Signed URL for uploading
        """
        self._ensure_initialized()
        blob = self._bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="PUT",
            content_type=content_type,
        )

        return url

    def generate_download_signed_url(
        self, blob_name: str, expiration_minutes: int = 60
    ) -> str:
        """Generate a signed URL for downloading a file.

        Args:
            blob_name: Name/path of the blob in GCS
            expiration_minutes: URL expiration time in minutes

        Returns:
            Signed URL for downloading
        """
        self._ensure_initialized()
        blob = self._bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4", expiration=timedelta(minutes=expiration_minutes), method="GET"
        )

        return url

    def delete_blob(self, blob_name: str) -> bool:
        """Delete a blob from GCS.

        Args:
            blob_name: Name/path of the blob to delete

        Returns:
            True if blob was deleted, False if not found
        """
        self._ensure_initialized()
        blob = self._bucket.blob(blob_name)

        if not blob.exists():
            return False

        blob.delete()
        return True

    def blob_exists(self, blob_name: str) -> bool:
        """Check if a blob exists in GCS.

        Args:
            blob_name: Name/path of the blob

        Returns:
            True if blob exists, False otherwise
        """
        self._ensure_initialized()
        blob = self._bucket.blob(blob_name)
        return blob.exists()

    def get_blob_metadata(self, blob_name: str) -> Optional[dict]:
        """Get metadata for a blob.

        Args:
            blob_name: Name/path of the blob

        Returns:
            Metadata dictionary if blob exists, None otherwise
        """
        self._ensure_initialized()
        blob = self._bucket.blob(blob_name)

        if not blob.exists():
            return None

        blob.reload()

        return {
            "name": blob.name,
            "size": blob.size,
            "content_type": blob.content_type,
            "created": blob.time_created,
            "updated": blob.updated,
        }


# Global GCS storage service instance (lazy initialization)
gcs_storage_service = GCSStorageService()
