"""
Unit tests for UploadCardUseCase
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.cards.upload_card import (
    UploadCardUseCase,
)
from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.services.card_validation_service import (
    CardValidationService,
)
from app.modules.social.domain.value_objects.upload_quota import (
    QuotaExceeded,
    UploadQuota,
)


class TestUploadCardUseCase:
    """Test UploadCardUseCase"""

    @pytest.fixture
    def mock_card_repository(self):
        """Create mock card repository"""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def mock_gcs_service(self):
        """Create mock GCS service"""
        service = Mock()
        service._bucket_name = "test-bucket"
        return service

    @pytest.fixture
    def validation_service(self):
        """Create validation service"""
        return CardValidationService()

    @pytest.fixture
    def use_case(self, mock_card_repository, mock_gcs_service, validation_service):
        """Create use case instance"""
        return UploadCardUseCase(
            card_repository=mock_card_repository,
            validation_service=validation_service,
            gcs_service=mock_gcs_service,
        )

    @pytest.fixture
    def free_quota(self):
        """Create free tier quota"""
        return UploadQuota.free_tier()

    @pytest.mark.asyncio
    async def test_upload_card_success(
        self, use_case, mock_card_repository, mock_gcs_service, free_quota
    ):
        """Test successful card upload"""
        # Arrange
        owner_id = uuid4()
        content_type = "image/jpeg"
        file_size_bytes = 1024 * 1024 * 5  # 5MB
        idol = "IU"
        idol_group = "Solo"
        album = "LILAC"
        version = "Standard"
        rarity = "rare"

        # Mock repository responses
        mock_card_repository.count_uploads_today.return_value = 0
        mock_card_repository.get_total_storage_used.return_value = 0

        # Create a mock card with ID
        saved_card = Card(
            id=uuid4(),
            owner_id=owner_id,
            idol=idol,
            idol_group=idol_group,
            album=album,
            version=version,
            rarity=rarity,
            size_bytes=file_size_bytes,
        )
        mock_card_repository.save.return_value = saved_card

        # Mock GCS signed URL generation
        mock_gcs_service.generate_upload_signed_url.return_value = (
            "https://storage.googleapis.com/test-bucket/cards/user/card.jpg?signature=abc"
        )

        # Act
        result = await use_case.execute(
            owner_id=owner_id,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            quota=free_quota,
            idol=idol,
            idol_group=idol_group,
            album=album,
            version=version,
            rarity=rarity,
        )

        # Assert
        assert result is not None
        assert result.method == "PUT"
        assert result.required_headers == {"Content-Type": content_type}
        assert result.card_id == saved_card.id
        assert "test-bucket" in result.image_url
        assert isinstance(result.expires_at, datetime)

        # Verify repository calls
        mock_card_repository.count_uploads_today.assert_called_once_with(owner_id)
        mock_card_repository.get_total_storage_used.assert_called_once_with(owner_id)
        assert mock_card_repository.save.call_count == 2  # Once for card creation, once for image update

        # Verify GCS call
        mock_gcs_service.generate_upload_signed_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_card_invalid_content_type(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test upload with invalid content type"""
        # Arrange
        owner_id = uuid4()
        content_type = "application/pdf"  # Not allowed
        file_size_bytes = 1024 * 1024

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid content type"):
            await use_case.execute(
                owner_id=owner_id,
                content_type=content_type,
                file_size_bytes=file_size_bytes,
                quota=free_quota,
            )

    @pytest.mark.asyncio
    async def test_upload_card_file_too_large(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test upload with file exceeding size limit"""
        # Arrange
        owner_id = uuid4()
        content_type = "image/jpeg"
        file_size_bytes = 1024 * 1024 * 20  # 20MB, exceeds 10MB limit

        # Act & Assert
        with pytest.raises(ValueError, match="File size exceeds limit"):
            await use_case.execute(
                owner_id=owner_id,
                content_type=content_type,
                file_size_bytes=file_size_bytes,
                quota=free_quota,
            )

    @pytest.mark.asyncio
    async def test_upload_card_daily_limit_exceeded(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test upload when daily limit is exceeded"""
        # Arrange
        owner_id = uuid4()
        content_type = "image/jpeg"
        file_size_bytes = 1024 * 1024 * 5

        # Mock that user has reached daily limit (2 uploads for free tier)
        mock_card_repository.count_uploads_today.return_value = 2

        # Act & Assert
        with pytest.raises(QuotaExceeded, match="Daily upload limit"):
            await use_case.execute(
                owner_id=owner_id,
                content_type=content_type,
                file_size_bytes=file_size_bytes,
                quota=free_quota,
            )

    @pytest.mark.asyncio
    async def test_upload_card_storage_limit_exceeded(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test upload when storage limit is exceeded"""
        # Arrange
        owner_id = uuid4()
        content_type = "image/jpeg"
        file_size_bytes = 1024 * 1024 * 5  # 5MB (within max file size)

        # Mock repository responses
        mock_card_repository.count_uploads_today.return_value = 0
        # Mock that user has used 1020MB out of 1024MB (free tier is 1GB)
        # Adding 5MB would exceed the limit (1020 + 5 = 1025 > 1024)
        mock_card_repository.get_total_storage_used.return_value = (
            1024 * 1024 * 1020
        )

        # Act & Assert
        with pytest.raises(QuotaExceeded, match="storage limit"):
            await use_case.execute(
                owner_id=owner_id,
                content_type=content_type,
                file_size_bytes=file_size_bytes,
                quota=free_quota,
            )

    @pytest.mark.asyncio
    async def test_upload_card_with_minimal_metadata(
        self, use_case, mock_card_repository, mock_gcs_service, free_quota
    ):
        """Test upload with only required fields"""
        # Arrange
        owner_id = uuid4()
        content_type = "image/png"
        file_size_bytes = 1024 * 1024 * 2  # 2MB

        # Mock repository responses
        mock_card_repository.count_uploads_today.return_value = 0
        mock_card_repository.get_total_storage_used.return_value = 0

        saved_card = Card(id=uuid4(), owner_id=owner_id, size_bytes=file_size_bytes)
        mock_card_repository.save.return_value = saved_card

        mock_gcs_service.generate_upload_signed_url.return_value = (
            "https://storage.googleapis.com/test-bucket/cards/user/card.png?signature=xyz"
        )

        # Act
        result = await use_case.execute(
            owner_id=owner_id,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            quota=free_quota,
        )

        # Assert
        assert result is not None
        assert result.card_id == saved_card.id
        assert ".png" in result.image_url

    @pytest.mark.asyncio
    async def test_upload_card_premium_quota(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test upload with premium quota allows more uploads"""
        # Arrange
        owner_id = uuid4()
        content_type = "image/jpeg"
        file_size_bytes = 1024 * 1024 * 5
        premium_quota = UploadQuota.premium_tier()

        # Mock that user has already uploaded many times today (but under premium limit)
        mock_card_repository.count_uploads_today.return_value = 100
        mock_card_repository.get_total_storage_used.return_value = 0

        saved_card = Card(id=uuid4(), owner_id=owner_id, size_bytes=file_size_bytes)
        mock_card_repository.save.return_value = saved_card

        mock_gcs_service.generate_upload_signed_url.return_value = (
            "https://storage.googleapis.com/test-bucket/cards/user/card.jpg?sig=abc"
        )

        # Act
        result = await use_case.execute(
            owner_id=owner_id,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            quota=premium_quota,
        )

        # Assert
        assert result is not None
        assert result.card_id == saved_card.id

    @pytest.mark.asyncio
    async def test_upload_card_generates_correct_blob_path(
        self, use_case, mock_card_repository, mock_gcs_service, free_quota
    ):
        """Test that blob path is generated correctly"""
        # Arrange
        owner_id = uuid4()
        content_type = "image/jpeg"
        file_size_bytes = 1024 * 1024

        mock_card_repository.count_uploads_today.return_value = 0
        mock_card_repository.get_total_storage_used.return_value = 0

        card_id = uuid4()
        saved_card = Card(id=card_id, owner_id=owner_id, size_bytes=file_size_bytes)
        mock_card_repository.save.return_value = saved_card

        mock_gcs_service.generate_upload_signed_url.return_value = (
            "https://storage.googleapis.com/test-bucket/signed-url"
        )

        # Act
        await use_case.execute(
            owner_id=owner_id,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            quota=free_quota,
        )

        # Assert
        # Check that generate_upload_signed_url was called with correct blob_name
        call_args = mock_gcs_service.generate_upload_signed_url.call_args
        blob_name = call_args.kwargs["blob_name"]
        assert blob_name == f"cards/{owner_id}/{card_id}.jpg"
        assert call_args.kwargs["content_type"] == content_type
        assert call_args.kwargs["expiration_minutes"] == 15
