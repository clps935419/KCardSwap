"""
Unit tests for UploadCardUseCase (T085)
Testing use case with mocked dependencies
"""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.cards.upload_card import (
    UploadCardResult,
    UploadCardUseCase,
)
from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.value_objects.upload_quota import (
    QuotaExceeded,
    UploadQuota,
)


class TestUploadCardUseCaseSuccess:
    """Test successful upload scenarios"""

    @pytest.fixture
    def mock_card_repository(self):
        """Mock card repository"""
        repo = Mock()
        repo.count_uploads_today = AsyncMock(return_value=0)
        repo.get_total_storage_used = AsyncMock(return_value=0)
        repo.save = AsyncMock(side_effect=lambda card: card)
        return repo

    @pytest.fixture
    def mock_validation_service(self):
        """Mock validation service"""
        service = Mock()
        service.validate_upload_request = Mock(return_value=(True, None))
        service.get_file_extension = Mock(return_value=".jpg")
        return service

    @pytest.fixture
    def mock_gcs_service(self):
        """Mock GCS storage service"""
        service = Mock()
        service._bucket_name = "kcardswap-test"
        service.generate_upload_signed_url = Mock(
            return_value="https://storage.googleapis.com/upload-url?signature=abc123"
        )
        return service

    @pytest.fixture
    def free_quota(self):
        """Free tier quota"""
        return UploadQuota.free_tier()

    @pytest.mark.asyncio
    async def test_upload_card_with_minimal_data(
        self, mock_card_repository, mock_validation_service, mock_gcs_service, free_quota
    ):
        """Test uploading card with only required fields"""
        use_case = UploadCardUseCase(
            card_repository=mock_card_repository,
            validation_service=mock_validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()
        content_type = "image/jpeg"
        file_size_bytes = 5 * 1024 * 1024  # 5MB

        result = await use_case.execute(
            owner_id=owner_id,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            quota=free_quota,
        )

        assert isinstance(result, UploadCardResult)
        assert result.upload_url.startswith("https://storage.googleapis.com/")
        assert result.method == "PUT"
        assert result.required_headers == {"Content-Type": content_type}
        assert result.image_url.startswith("https://storage.googleapis.com/")
        assert isinstance(result.card_id, type(uuid4()))
        assert isinstance(result.expires_at, datetime)

        # Verify repository interactions
        mock_card_repository.count_uploads_today.assert_called_once_with(owner_id)
        mock_card_repository.get_total_storage_used.assert_called_once_with(owner_id)
        assert mock_card_repository.save.call_count == 2  # Once for creation, once for update

    @pytest.mark.asyncio
    async def test_upload_card_with_metadata(
        self, mock_card_repository, mock_validation_service, mock_gcs_service, free_quota
    ):
        """Test uploading card with full metadata"""
        use_case = UploadCardUseCase(
            card_repository=mock_card_repository,
            validation_service=mock_validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()

        result = await use_case.execute(
            owner_id=owner_id,
            content_type="image/jpeg",
            file_size_bytes=3 * 1024 * 1024,
            quota=free_quota,
            idol="IU",
            idol_group="Solo",
            album="LILAC",
            version="Standard",
            rarity=Card.RARITY_RARE,
        )

        assert isinstance(result, UploadCardResult)
        assert result.card_id is not None

    @pytest.mark.asyncio
    async def test_upload_generates_correct_blob_path(
        self, mock_card_repository, mock_validation_service, mock_gcs_service, free_quota
    ):
        """Test that GCS blob path follows correct format"""
        use_case = UploadCardUseCase(
            card_repository=mock_card_repository,
            validation_service=mock_validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()

        result = await use_case.execute(
            owner_id=owner_id,
            content_type="image/png",
            file_size_bytes=2 * 1024 * 1024,
            quota=free_quota,
        )

        # Check that image_url follows pattern: cards/{user_id}/{card_id}.jpg
        assert f"cards/{owner_id}/" in result.image_url
        assert result.card_id is not None

    @pytest.mark.asyncio
    async def test_upload_url_expiration(
        self, mock_card_repository, mock_validation_service, mock_gcs_service, free_quota
    ):
        """Test that upload URL has 15-minute expiration"""
        use_case = UploadCardUseCase(
            card_repository=mock_card_repository,
            validation_service=mock_validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()
        before_execution = datetime.utcnow()

        result = await use_case.execute(
            owner_id=owner_id,
            content_type="image/jpeg",
            file_size_bytes=1 * 1024 * 1024,
            quota=free_quota,
        )

        after_execution = datetime.utcnow()

        # Expiration should be ~15 minutes from now
        expected_min = before_execution + timedelta(minutes=15)
        expected_max = after_execution + timedelta(minutes=15)

        assert expected_min <= result.expires_at <= expected_max


class TestUploadCardUseCaseValidation:
    """Test validation failures"""

    @pytest.fixture
    def mock_card_repository(self):
        """Mock card repository"""
        repo = Mock()
        repo.count_uploads_today = AsyncMock(return_value=0)
        repo.get_total_storage_used = AsyncMock(return_value=0)
        return repo

    @pytest.fixture
    def mock_gcs_service(self):
        """Mock GCS service"""
        service = Mock()
        service._bucket_name = "kcardswap-test"
        return service

    @pytest.mark.asyncio
    async def test_upload_fails_invalid_content_type(
        self, mock_card_repository, mock_gcs_service
    ):
        """Test upload fails for invalid content type"""
        validation_service = Mock()
        validation_service.validate_upload_request = Mock(
            return_value=(False, "Invalid content type. Must be image/jpeg or image/png")
        )

        use_case = UploadCardUseCase(
            card_repository=mock_card_repository,
            validation_service=validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()
        quota = UploadQuota.free_tier()

        with pytest.raises(ValueError, match="Invalid content type"):
            await use_case.execute(
                owner_id=owner_id,
                content_type="image/gif",  # Invalid
                file_size_bytes=1 * 1024 * 1024,
                quota=quota,
            )

    @pytest.mark.asyncio
    async def test_upload_fails_file_too_large(
        self, mock_card_repository, mock_gcs_service
    ):
        """Test upload fails for oversized file"""
        validation_service = Mock()
        validation_service.validate_upload_request = Mock(
            return_value=(False, "File size exceeds maximum of 10MB")
        )

        use_case = UploadCardUseCase(
            card_repository=mock_card_repository,
            validation_service=validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()
        quota = UploadQuota.free_tier()

        with pytest.raises(ValueError, match="File size exceeds"):
            await use_case.execute(
                owner_id=owner_id,
                content_type="image/jpeg",
                file_size_bytes=15 * 1024 * 1024,  # 15MB - too large
                quota=quota,
            )


class TestUploadCardUseCaseQuotaLimits:
    """Test quota limit enforcement"""

    @pytest.fixture
    def mock_validation_service(self):
        """Mock validation service (always passes)"""
        service = Mock()
        service.validate_upload_request = Mock(return_value=(True, None))
        service.get_file_extension = Mock(return_value=".jpg")
        return service

    @pytest.fixture
    def mock_gcs_service(self):
        """Mock GCS service"""
        service = Mock()
        service._bucket_name = "kcardswap-test"
        return service

    @pytest.mark.asyncio
    async def test_upload_fails_daily_limit_exceeded(
        self, mock_validation_service, mock_gcs_service
    ):
        """Test upload fails when daily limit is exceeded"""
        # Mock repository showing user has already uploaded 2 times today
        mock_repo = Mock()
        mock_repo.count_uploads_today = AsyncMock(return_value=2)  # At limit
        mock_repo.get_total_storage_used = AsyncMock(return_value=0)

        use_case = UploadCardUseCase(
            card_repository=mock_repo,
            validation_service=mock_validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()
        quota = UploadQuota.free_tier()  # daily_limit = 2

        with pytest.raises(QuotaExceeded) as exc_info:
            await use_case.execute(
                owner_id=owner_id,
                content_type="image/jpeg",
                file_size_bytes=1 * 1024 * 1024,
                quota=quota,
            )

        assert exc_info.value.limit_type == "daily"
        assert "Daily upload limit" in exc_info.value.reason

    @pytest.mark.asyncio
    async def test_upload_fails_storage_limit_exceeded(
        self, mock_validation_service, mock_gcs_service
    ):
        """Test upload fails when storage limit is exceeded"""
        # Mock repository showing user has used 950MB of 1GB
        mock_repo = Mock()
        mock_repo.count_uploads_today = AsyncMock(return_value=0)
        mock_repo.get_total_storage_used = AsyncMock(
            return_value=950 * 1024 * 1024  # 950MB used
        )

        use_case = UploadCardUseCase(
            card_repository=mock_repo,
            validation_service=mock_validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()
        quota = UploadQuota.free_tier()  # total_storage = 1GB

        # Try to upload 100MB file (would exceed 1GB total)
        with pytest.raises(QuotaExceeded) as exc_info:
            await use_case.execute(
                owner_id=owner_id,
                content_type="image/jpeg",
                file_size_bytes=100 * 1024 * 1024,
                quota=quota,
            )

        assert exc_info.value.limit_type == "storage"
        assert "Total storage limit" in exc_info.value.reason

    @pytest.mark.asyncio
    async def test_upload_succeeds_just_under_daily_limit(
        self, mock_validation_service, mock_gcs_service
    ):
        """Test upload succeeds when just under daily limit"""
        # Mock repository showing user has uploaded 1 time today
        mock_repo = Mock()
        mock_repo.count_uploads_today = AsyncMock(return_value=1)  # 1 of 2 used
        mock_repo.get_total_storage_used = AsyncMock(return_value=0)
        mock_repo.save = AsyncMock(side_effect=lambda card: card)

        mock_gcs_service.generate_upload_signed_url = Mock(
            return_value="https://storage.googleapis.com/upload"
        )

        use_case = UploadCardUseCase(
            card_repository=mock_repo,
            validation_service=mock_validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()
        quota = UploadQuota.free_tier()  # daily_limit = 2

        # This should succeed (2nd upload of the day)
        result = await use_case.execute(
            owner_id=owner_id,
            content_type="image/jpeg",
            file_size_bytes=1 * 1024 * 1024,
            quota=quota,
        )

        assert isinstance(result, UploadCardResult)

    @pytest.mark.asyncio
    async def test_upload_succeeds_just_under_storage_limit(
        self, mock_validation_service, mock_gcs_service
    ):
        """Test upload succeeds when just under storage limit"""
        # Mock repository showing user has used 900MB of 1GB
        mock_repo = Mock()
        mock_repo.count_uploads_today = AsyncMock(return_value=0)
        mock_repo.get_total_storage_used = AsyncMock(
            return_value=900 * 1024 * 1024  # 900MB used
        )
        mock_repo.save = AsyncMock(side_effect=lambda card: card)

        mock_gcs_service.generate_upload_signed_url = Mock(
            return_value="https://storage.googleapis.com/upload"
        )

        use_case = UploadCardUseCase(
            card_repository=mock_repo,
            validation_service=mock_validation_service,
            gcs_service=mock_gcs_service,
        )

        owner_id = uuid4()
        quota = UploadQuota.free_tier()  # total_storage = 1GB

        # Upload 50MB file (total = 950MB, still under 1GB)
        result = await use_case.execute(
            owner_id=owner_id,
            content_type="image/jpeg",
            file_size_bytes=50 * 1024 * 1024,
            quota=quota,
        )

        assert isinstance(result, UploadCardResult)
