"""Pytest fixtures for media module integration tests."""

import pytest
import pytest_asyncio

from app.modules.media.application.use_cases.attach_media import AttachMediaUseCase
from app.modules.media.application.use_cases.confirm_upload import (
    ConfirmUploadUseCase,
)
from app.modules.media.application.use_cases.create_upload_url import (
    CreateUploadUrlUseCase,
)
from app.modules.media.infrastructure.repositories.media_repository_impl import (
    MediaRepositoryImpl,
)
from app.shared.domain.quota.media_quota_service import MediaQuotaService
from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)


@pytest_asyncio.fixture
async def test_user_id(create_user):
    """Test user ID fixture (persisted in DB)."""
    return await create_user("media")


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
def subscription_query_service(db_session):
    """Subscription query service fixture for media quota checks."""
    from app.modules.identity.application.services.subscription_query_service_impl import (
        SubscriptionQueryServiceImpl,
    )
    from app.modules.identity.infrastructure.repositories.subscription_repository_impl import (
        SubscriptionRepositoryImpl,
    )

    repo = SubscriptionRepositoryImpl(db_session)
    return SubscriptionQueryServiceImpl(subscription_repository=repo)


@pytest.fixture
def create_upload_url_use_case(media_repository, mock_gcs_storage, media_quota_service):
    """Create upload URL use case fixture."""
    return CreateUploadUrlUseCase(
        media_repository=media_repository,
        storage_service=mock_gcs_storage,
        media_quota_service=media_quota_service,
    )


@pytest.fixture
def confirm_upload_use_case(media_repository, media_quota_service, mock_gcs_storage):
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
