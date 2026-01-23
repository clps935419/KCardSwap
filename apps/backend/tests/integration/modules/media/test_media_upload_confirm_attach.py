"""Integration tests for media upload, confirm, and attach flow.

Tests User Story 3 - Media Upload & Attach (T045).
"""
import pytest
from uuid import uuid4

from app.modules.media.application.use_cases.attach_media import (
    AttachMediaRequest,
    AttachMediaUseCase,
)
from app.modules.media.application.use_cases.confirm_upload import (
    ConfirmUploadRequest,
    ConfirmUploadUseCase,
)
from app.modules.media.application.use_cases.create_upload_url import (
    CreateUploadUrlRequest,
    CreateUploadUrlUseCase,
)
from app.modules.media.domain.entities.media_asset import MediaStatus
from app.modules.media.domain.repositories.i_media_repository import IMediaRepository
from app.shared.infrastructure.external.gcs_storage_service import GCSStorageService
from app.shared.presentation.errors.limit_exceeded import LimitExceededException


@pytest.mark.asyncio
class TestMediaUploadConfirmAttach:
    """Test media upload flow: presign → upload → confirm → attach."""

    async def test_create_upload_url_success(
        self,
        create_upload_url_use_case: CreateUploadUrlUseCase,
        test_user_id,
    ):
        """Test presign URL generation."""
        request = CreateUploadUrlRequest(
            user_id=test_user_id,
            content_type="image/jpeg",
            file_size_bytes=512000,  # 500KB
            filename="test.jpg",
        )

        result = await create_upload_url_use_case.execute(request)

        assert result.media_id is not None
        assert result.upload_url is not None
        assert "media/" in result.upload_url
        assert result.expires_in_minutes == 15

    async def test_confirm_upload_success(
        self,
        create_upload_url_use_case: CreateUploadUrlUseCase,
        confirm_upload_use_case: ConfirmUploadUseCase,
        media_repository: IMediaRepository,
        mock_gcs_storage: GCSStorageService,
        test_user_id,
    ):
        """Test upload confirmation with quota check."""
        # Step 1: Create presign URL
        presign_request = CreateUploadUrlRequest(
            user_id=test_user_id,
            content_type="image/png",
            file_size_bytes=768000,  # 750KB
        )
        presign_result = await create_upload_url_use_case.execute(presign_request)

        # Simulate upload to GCS (mock stores blob)
        mock_gcs_storage._mock_storage[presign_result.gcs_blob_name] = {
            "size": 768000,
            "content_type": "image/png",
        }

        # Step 2: Confirm upload
        confirm_request = ConfirmUploadRequest(
            user_id=test_user_id,
            media_id=presign_result.media_id,
        )
        confirm_result = await confirm_upload_use_case.execute(confirm_request)

        assert confirm_result.media_id == presign_result.media_id
        assert confirm_result.status == MediaStatus.CONFIRMED.value
        assert confirm_result.file_size_bytes == 768000

        # Verify media in database
        media = await media_repository.get_by_id(presign_result.media_id)
        assert media is not None
        assert media.status == MediaStatus.CONFIRMED
        assert media.confirmed_at is not None

    async def test_confirm_upload_blob_not_exists(
        self,
        create_upload_url_use_case: CreateUploadUrlUseCase,
        confirm_upload_use_case: ConfirmUploadUseCase,
        test_user_id,
    ):
        """Test confirmation fails if blob doesn't exist in GCS."""
        # Create presign URL but don't upload
        presign_request = CreateUploadUrlRequest(
            user_id=test_user_id,
            content_type="image/jpeg",
            file_size_bytes=512000,
        )
        presign_result = await create_upload_url_use_case.execute(presign_request)

        # Try to confirm without uploading
        confirm_request = ConfirmUploadRequest(
            user_id=test_user_id,
            media_id=presign_result.media_id,
        )

        with pytest.raises(ValueError, match="Media file not found in storage"):
            await confirm_upload_use_case.execute(confirm_request)

    async def test_confirm_upload_exceeds_file_size_quota(
        self,
        create_upload_url_use_case: CreateUploadUrlUseCase,
        confirm_upload_use_case: ConfirmUploadUseCase,
        mock_gcs_storage: GCSStorageService,
        test_user_id,
    ):
        """Test confirmation fails if file size exceeds quota (1MB for free users)."""
        # Create presign URL for file larger than quota
        large_file_size = 2 * 1024 * 1024  # 2MB (exceeds 1MB free tier limit)
        presign_request = CreateUploadUrlRequest(
            user_id=test_user_id,
            content_type="image/jpeg",
            file_size_bytes=large_file_size,
        )
        presign_result = await create_upload_url_use_case.execute(presign_request)

        # Simulate upload
        mock_gcs_storage._mock_storage[presign_result.gcs_blob_name] = {
            "size": large_file_size,
            "content_type": "image/jpeg",
        }

        # Try to confirm - should fail with quota exceeded
        confirm_request = ConfirmUploadRequest(
            user_id=test_user_id,
            media_id=presign_result.media_id,
        )

        with pytest.raises(LimitExceededException) as exc_info:
            await confirm_upload_use_case.execute(confirm_request)

        assert exc_info.value.limit_key == "media_file_bytes_max"
        assert exc_info.value.limit_value == 1 * 1024 * 1024  # 1MB for free users

    async def test_attach_media_to_post_success(
        self,
        create_upload_url_use_case: CreateUploadUrlUseCase,
        confirm_upload_use_case: ConfirmUploadUseCase,
        attach_media_use_case: AttachMediaUseCase,
        mock_gcs_storage: GCSStorageService,
        media_repository: IMediaRepository,
        test_user_id,
    ):
        """Test attaching confirmed media to post."""
        # Step 1: Presign
        presign_request = CreateUploadUrlRequest(
            user_id=test_user_id,
            content_type="image/jpeg",
            file_size_bytes=512000,
        )
        presign_result = await create_upload_url_use_case.execute(presign_request)

        # Step 2: Upload (simulate)
        mock_gcs_storage._mock_storage[presign_result.gcs_blob_name] = {
            "size": 512000,
            "content_type": "image/jpeg",
        }

        # Step 3: Confirm
        confirm_request = ConfirmUploadRequest(
            user_id=test_user_id,
            media_id=presign_result.media_id,
        )
        await confirm_upload_use_case.execute(confirm_request)

        # Step 4: Attach to post
        post_id = uuid4()
        attach_request = AttachMediaRequest(
            user_id=test_user_id,
            media_id=presign_result.media_id,
            target_type="post",
            target_id=post_id,
        )
        attach_result = await attach_media_use_case.execute(attach_request)

        assert attach_result.media_id == presign_result.media_id
        assert attach_result.status == MediaStatus.ATTACHED.value
        assert attach_result.attached_to == "post"
        assert attach_result.target_id == post_id

        # Verify status in database
        media = await media_repository.get_by_id(presign_result.media_id)
        assert media.status == MediaStatus.ATTACHED

    async def test_attach_media_not_confirmed_fails(
        self,
        create_upload_url_use_case: CreateUploadUrlUseCase,
        attach_media_use_case: AttachMediaUseCase,
        test_user_id,
    ):
        """Test attaching media fails if not confirmed (FR-007)."""
        # Create presign URL but don't confirm
        presign_request = CreateUploadUrlRequest(
            user_id=test_user_id,
            content_type="image/jpeg",
            file_size_bytes=512000,
        )
        presign_result = await create_upload_url_use_case.execute(presign_request)

        # Try to attach without confirming
        post_id = uuid4()
        attach_request = AttachMediaRequest(
            user_id=test_user_id,
            media_id=presign_result.media_id,
            target_type="post",
            target_id=post_id,
        )

        with pytest.raises(ValueError, match="must be confirmed before attaching"):
            await attach_media_use_case.execute(attach_request)

    async def test_attach_media_wrong_owner_fails(
        self,
        create_upload_url_use_case: CreateUploadUrlUseCase,
        confirm_upload_use_case: ConfirmUploadUseCase,
        attach_media_use_case: AttachMediaUseCase,
        mock_gcs_storage: GCSStorageService,
        test_user_id,
    ):
        """Test attaching media fails if user is not the owner (FR-007)."""
        # User 1 creates and confirms media
        presign_request = CreateUploadUrlRequest(
            user_id=test_user_id,
            content_type="image/jpeg",
            file_size_bytes=512000,
        )
        presign_result = await create_upload_url_use_case.execute(presign_request)

        mock_gcs_storage._mock_storage[presign_result.gcs_blob_name] = {
            "size": 512000,
            "content_type": "image/jpeg",
        }

        confirm_request = ConfirmUploadRequest(
            user_id=test_user_id,
            media_id=presign_result.media_id,
        )
        await confirm_upload_use_case.execute(confirm_request)

        # User 2 tries to attach user 1's media
        other_user_id = uuid4()
        post_id = uuid4()
        attach_request = AttachMediaRequest(
            user_id=other_user_id,
            media_id=presign_result.media_id,
            target_type="post",
            target_id=post_id,
        )

        with pytest.raises(ValueError, match="is not owned by user"):
            await attach_media_use_case.execute(attach_request)

    async def test_monthly_quota_tracking(
        self,
        create_upload_url_use_case: CreateUploadUrlUseCase,
        confirm_upload_use_case: ConfirmUploadUseCase,
        mock_gcs_storage: GCSStorageService,
        media_repository: IMediaRepository,
        test_user_id,
    ):
        """Test monthly bytes quota is tracked correctly."""
        from datetime import datetime

        # Upload first media (500KB)
        presign1 = await create_upload_url_use_case.execute(
            CreateUploadUrlRequest(
                user_id=test_user_id,
                content_type="image/jpeg",
                file_size_bytes=512000,
            )
        )
        mock_gcs_storage._mock_storage[presign1.gcs_blob_name] = {"size": 512000, "content_type": "image/jpeg"}
        await confirm_upload_use_case.execute(
            ConfirmUploadRequest(user_id=test_user_id, media_id=presign1.media_id)
        )

        # Upload second media (400KB)
        presign2 = await create_upload_url_use_case.execute(
            CreateUploadUrlRequest(
                user_id=test_user_id,
                content_type="image/png",
                file_size_bytes=409600,
            )
        )
        mock_gcs_storage._mock_storage[presign2.gcs_blob_name] = {"size": 409600, "content_type": "image/png"}
        await confirm_upload_use_case.execute(
            ConfirmUploadRequest(user_id=test_user_id, media_id=presign2.media_id)
        )

        # Check monthly usage
        now = datetime.utcnow()
        monthly_usage = await media_repository.get_monthly_bytes_used(
            user_id=test_user_id,
            year=now.year,
            month=now.month,
        )

        assert monthly_usage == 512000 + 409600  # Total confirmed bytes
