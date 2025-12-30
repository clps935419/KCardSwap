"""
Unit tests for CheckUploadQuotaUseCase
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.cards.check_quota import (
    CheckUploadQuotaUseCase,
    QuotaStatus,
)
from app.modules.social.domain.value_objects.upload_quota import UploadQuota


class TestQuotaStatus:
    """Test QuotaStatus data class"""

    def test_quota_status_creation(self):
        """Test creating QuotaStatus"""
        # Arrange & Act
        status = QuotaStatus(
            uploads_today=1,
            daily_limit=2,
            remaining_uploads=1,
            storage_used_bytes=1024 * 1024 * 100,  # 100MB
            storage_limit_bytes=1024 * 1024 * 1024,  # 1GB
            remaining_storage_bytes=1024 * 1024 * 924,  # 924MB
        )

        # Assert
        assert status.uploads_today == 1
        assert status.daily_limit == 2
        assert status.remaining_uploads == 1
        assert status.storage_used_bytes == 1024 * 1024 * 100
        assert status.storage_limit_bytes == 1024 * 1024 * 1024
        assert status.remaining_storage_bytes == 1024 * 1024 * 924

    def test_quota_status_to_dict(self):
        """Test converting QuotaStatus to dictionary"""
        # Arrange
        status = QuotaStatus(
            uploads_today=1,
            daily_limit=2,
            remaining_uploads=1,
            storage_used_bytes=1024 * 1024 * 100,  # 100MB
            storage_limit_bytes=1024 * 1024 * 1024,  # 1GB
            remaining_storage_bytes=1024 * 1024 * 924,  # 924MB
        )

        # Act
        result = status.to_dict()

        # Assert
        assert result["uploads_today"] == 1
        assert result["daily_limit"] == 2
        assert result["remaining_uploads"] == 1
        assert result["storage_used_bytes"] == 1024 * 1024 * 100
        assert result["storage_limit_bytes"] == 1024 * 1024 * 1024
        assert result["remaining_storage_bytes"] == 1024 * 1024 * 924
        assert result["storage_used_mb"] == 100.0
        assert result["storage_limit_mb"] == 1024.0
        assert result["remaining_storage_mb"] == 924.0

    def test_quota_status_to_dict_with_fractional_mb(self):
        """Test to_dict with fractional MB values"""
        # Arrange
        status = QuotaStatus(
            uploads_today=0,
            daily_limit=2,
            remaining_uploads=2,
            storage_used_bytes=1024 * 1024 * 50 + 512 * 1024,  # 50.5MB
            storage_limit_bytes=1024 * 1024 * 1024,  # 1GB
            remaining_storage_bytes=1024 * 1024 * 973 + 512 * 1024,  # 973.5MB
        )

        # Act
        result = status.to_dict()

        # Assert
        assert result["storage_used_mb"] == 50.5
        assert result["remaining_storage_mb"] == 973.5


class TestCheckUploadQuotaUseCase:
    """Test CheckUploadQuotaUseCase"""

    @pytest.fixture
    def mock_card_repository(self):
        """Create mock card repository"""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def use_case(self, mock_card_repository):
        """Create use case instance"""
        return CheckUploadQuotaUseCase(card_repository=mock_card_repository)

    @pytest.fixture
    def free_quota(self):
        """Create free tier quota"""
        return UploadQuota.free_tier()

    @pytest.fixture
    def premium_quota(self):
        """Create premium tier quota"""
        return UploadQuota.premium_tier()

    @pytest.mark.asyncio
    async def test_check_quota_no_usage(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test checking quota when user has not uploaded anything"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 0
        mock_card_repository.get_total_storage_used.return_value = 0

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)

        # Assert
        assert isinstance(result, QuotaStatus)
        assert result.uploads_today == 0
        assert result.daily_limit == 2
        assert result.remaining_uploads == 2
        assert result.storage_used_bytes == 0
        assert result.storage_limit_bytes == 1024 * 1024 * 1024  # 1GB
        assert result.remaining_storage_bytes == 1024 * 1024 * 1024
        mock_card_repository.count_uploads_today.assert_called_once_with(owner_id)
        mock_card_repository.get_total_storage_used.assert_called_once_with(owner_id)

    @pytest.mark.asyncio
    async def test_check_quota_partial_usage(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test checking quota with partial usage"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 1
        mock_card_repository.get_total_storage_used.return_value = (
            1024 * 1024 * 500
        )  # 500MB

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)

        # Assert
        assert result.uploads_today == 1
        assert result.daily_limit == 2
        assert result.remaining_uploads == 1
        assert result.storage_used_bytes == 1024 * 1024 * 500
        assert result.remaining_storage_bytes == 1024 * 1024 * 524  # ~524MB remaining

    @pytest.mark.asyncio
    async def test_check_quota_daily_limit_reached(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test checking quota when daily limit is reached"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 2  # Limit is 2
        mock_card_repository.get_total_storage_used.return_value = 1024 * 1024 * 100

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)

        # Assert
        assert result.uploads_today == 2
        assert result.daily_limit == 2
        assert result.remaining_uploads == 0

    @pytest.mark.asyncio
    async def test_check_quota_daily_limit_exceeded(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test checking quota when daily limit is exceeded (edge case)"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 3  # Over limit
        mock_card_repository.get_total_storage_used.return_value = 0

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)

        # Assert
        assert result.uploads_today == 3
        assert result.remaining_uploads == 0  # Should not be negative

    @pytest.mark.asyncio
    async def test_check_quota_storage_nearly_full(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test checking quota when storage is nearly full"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 1
        # 950MB used out of 1GB
        mock_card_repository.get_total_storage_used.return_value = (
            1024 * 1024 * 1024 - 1024 * 1024 * 50
        )

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)

        # Assert
        assert result.storage_used_bytes == 1024 * 1024 * 1024 - 1024 * 1024 * 50
        assert result.remaining_storage_bytes == 1024 * 1024 * 50  # ~50MB remaining

    @pytest.mark.asyncio
    async def test_check_quota_storage_full(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test checking quota when storage is full"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 0
        mock_card_repository.get_total_storage_used.return_value = (
            1024 * 1024 * 1024
        )  # 1GB

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)

        # Assert
        assert result.storage_used_bytes == 1024 * 1024 * 1024
        assert result.remaining_storage_bytes == 0

    @pytest.mark.asyncio
    async def test_check_quota_storage_exceeded(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test checking quota when storage is exceeded (edge case)"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 0
        # More than 1GB (edge case - shouldn't happen but handle gracefully)
        mock_card_repository.get_total_storage_used.return_value = (
            1024 * 1024 * 1024 + 1024 * 1024 * 100
        )

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)

        # Assert
        assert result.storage_used_bytes > result.storage_limit_bytes
        assert result.remaining_storage_bytes == 0  # Should not be negative

    @pytest.mark.asyncio
    async def test_check_quota_premium_tier(
        self, use_case, mock_card_repository, premium_quota
    ):
        """Test checking quota with premium tier"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 100  # Many uploads
        mock_card_repository.get_total_storage_used.return_value = (
            1024 * 1024 * 1024 * 5
        )  # 5GB

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=premium_quota)

        # Assert
        assert result.uploads_today == 100
        assert result.daily_limit == 999999  # Effectively unlimited
        assert result.remaining_uploads > 0
        assert result.storage_used_bytes == 1024 * 1024 * 1024 * 5
        assert result.storage_limit_bytes == 1024 * 1024 * 1024 * 10  # 10GB
        assert result.remaining_storage_bytes == 1024 * 1024 * 1024 * 5

    @pytest.mark.asyncio
    async def test_check_quota_custom_quota(
        self, use_case, mock_card_repository
    ):
        """Test checking quota with custom quota values"""
        # Arrange
        owner_id = uuid4()
        custom_quota = UploadQuota.from_mb_gb(
            daily_limit=5,
            max_file_mb=20,
            total_storage_gb=5,
        )
        mock_card_repository.count_uploads_today.return_value = 3
        mock_card_repository.get_total_storage_used.return_value = (
            1024 * 1024 * 1024 * 2
        )  # 2GB

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=custom_quota)

        # Assert
        assert result.uploads_today == 3
        assert result.daily_limit == 5
        assert result.remaining_uploads == 2
        assert result.storage_used_bytes == 1024 * 1024 * 1024 * 2
        assert result.storage_limit_bytes == 1024 * 1024 * 1024 * 5
        assert result.remaining_storage_bytes == 1024 * 1024 * 1024 * 3

    @pytest.mark.asyncio
    async def test_check_quota_zero_storage_used(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test checking quota with zero storage used"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 0
        mock_card_repository.get_total_storage_used.return_value = 0

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)

        # Assert
        assert result.storage_used_bytes == 0
        assert result.remaining_storage_bytes == result.storage_limit_bytes

    @pytest.mark.asyncio
    async def test_check_quota_to_dict_integration(
        self, use_case, mock_card_repository, free_quota
    ):
        """Test that QuotaStatus can be converted to dict for API response"""
        # Arrange
        owner_id = uuid4()
        mock_card_repository.count_uploads_today.return_value = 1
        mock_card_repository.get_total_storage_used.return_value = 1024 * 1024 * 200

        # Act
        result = await use_case.execute(owner_id=owner_id, quota=free_quota)
        result_dict = result.to_dict()

        # Assert
        assert "uploads_today" in result_dict
        assert "daily_limit" in result_dict
        assert "remaining_uploads" in result_dict
        assert "storage_used_bytes" in result_dict
        assert "storage_limit_bytes" in result_dict
        assert "remaining_storage_bytes" in result_dict
        assert "storage_used_mb" in result_dict
        assert "storage_limit_mb" in result_dict
        assert "remaining_storage_mb" in result_dict
