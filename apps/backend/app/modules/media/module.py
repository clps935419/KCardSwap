"""Media Module - Dependency Injection Configuration."""
from injector import Binder, Module, singleton
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.shared.domain.quota.media_quota_service import MediaQuotaService
from app.shared.infrastructure.external.gcs_storage_service import GCSStorageService


class MediaModule(Module):
    """Media module dependency injection configuration."""

    def configure(self, binder: Binder) -> None:
        """Configure media module dependencies.
        
        Args:
            binder: Injector binder for dependency configuration
        """
        # Repository bindings
        binder.bind(
            IMediaRepository,
            to=MediaRepositoryImpl,
            scope=singleton,
        )

        # Use case bindings
        binder.bind(CreateUploadUrlUseCase, to=CreateUploadUrlUseCase, scope=singleton)
        binder.bind(ConfirmUploadUseCase, to=ConfirmUploadUseCase, scope=singleton)
        binder.bind(AttachMediaUseCase, to=AttachMediaUseCase, scope=singleton)

        # Note: MediaQuotaService and GCSStorageService are provided by SharedModule
