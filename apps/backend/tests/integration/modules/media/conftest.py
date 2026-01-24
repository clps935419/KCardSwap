"""Pytest fixtures for media module integration tests."""
import pytest
from uuid import uuid4

from app.modules.media.application.use_cases.attach_media import AttachMediaUseCase
from app.modules.media.application.use_cases.confirm_upload import (
    ConfirmUploadUseCase,
)
from app.modules.media.application.use_cases.create_upload_url import (
    CreateUploadUrlUseCase,
)
from app.modules.media.domain.repositories.i_media_repository import IMediaRepository
from app.modules.media.infrastructure.repositories.media_repository_impl import (
    MediaRepositoryImpl,
)
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)
from app.shared.domain.quota.media_quota_service import MediaQuotaService
from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)


@pytest.fixture
def test_user_id():
    """Test user ID fixture."""
    return uuid4()


@pytest.fixture
def mock_gcs_storage():
    """Mock GCS storage service fixture."""
    return MockGCSStorageService()


@pytest.fixture
def media_repository(db_session):
    """Media repository fixture."""
    return MediaRepositoryImpl(db_session)


@pytest.fixture
def media_quota_service(subscription_query_service):
    """Media quota service fixture."""
    return MediaQuotaService(subscription_query_service)


@pytest.fixture
def create_upload_url_use_case(media_repository, mock_gcs_storage):
    """Create upload URL use case fixture."""
    return CreateUploadUrlUseCase(
        media_repository=media_repository,
        storage_service=mock_gcs_storage,
    )


@pytest.fixture
def confirm_upload_use_case(
    media_repository, media_quota_service, mock_gcs_storage
):
    """Confirm upload use case fixture."""
    return ConfirmUploadUseCase(
        media_repository=media_repository,
        media_quota_service=media_quota_service,
        storage_service=mock_gcs_storage,
    )


@pytest.fixture
def attach_media_use_case(media_repository):
    """Attach media use case fixture."""
    return AttachMediaUseCase(
        media_repository=media_repository,
    )
