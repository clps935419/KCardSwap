"""Storage service factory for GCS.

This module provides a factory to get the appropriate storage service
(real or mock) based on the application configuration.
"""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from app.shared.infrastructure.external.gcs_storage_service import (
        GCSStorageService,
    )

from app.config import settings
from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)


def get_storage_service() -> Union["GCSStorageService", MockGCSStorageService]:
    """Get the appropriate storage service based on configuration.

    Returns:
        MockGCSStorageService if USE_MOCK_GCS is true (default for dev/test)
        GCSStorageService if USE_MOCK_GCS is false (production/staging)

    The service selection is based on the USE_MOCK_GCS environment variable:
    - Development/Testing: USE_MOCK_GCS=true (default) → MockGCSStorageService
    - Production/Staging: USE_MOCK_GCS=false → GCSStorageService
    """
    if settings.USE_MOCK_GCS:
        return MockGCSStorageService(
            bucket_name=settings.GCS_BUCKET_NAME,
            credentials_path=settings.GCS_CREDENTIALS_PATH,
        )
    else:
        # Import only when needed to avoid dependency issues in development
        from app.shared.infrastructure.external.gcs_storage_service import (
            GCSStorageService,
        )

        return GCSStorageService(
            bucket_name=settings.GCS_BUCKET_NAME,
            credentials_path=settings.GCS_CREDENTIALS_PATH,
        )


# Global storage service instance (uses factory)
storage_service = get_storage_service()
