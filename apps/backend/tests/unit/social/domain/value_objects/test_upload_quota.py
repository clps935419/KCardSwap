"""
Unit tests for UploadQuota Value Object

Tests the upload quota value object for users.
"""

import pytest

from app.modules.social.domain.value_objects.upload_quota import (
    QuotaExceededError,
    UploadQuota,
)


class TestUploadQuota:
    """Test UploadQuota value object"""

    def test_init_valid(self):
        """Test creating a valid upload quota"""
        # Act
        quota = UploadQuota(
            daily_limit=5,
            max_file_size_bytes=10 * 1024 * 1024,
            total_storage_bytes=1 * 1024 * 1024 * 1024,
        )

        # Assert
        assert quota.daily_limit == 5
        assert quota.max_file_size_bytes == 10 * 1024 * 1024
        assert quota.total_storage_bytes == 1 * 1024 * 1024 * 1024

    def test_init_negative_daily_limit(self):
        """Test that negative daily limit raises error"""
        # Act & Assert
        with pytest.raises(ValueError, match="daily_limit must be non-negative"):
            UploadQuota(
                daily_limit=-1,
                max_file_size_bytes=1000,
                total_storage_bytes=1000,
            )

    def test_init_zero_max_file_size(self):
        """Test that zero max file size raises error"""
        # Act & Assert
        with pytest.raises(ValueError, match="max_file_size_bytes must be positive"):
            UploadQuota(
                daily_limit=5,
                max_file_size_bytes=0,
                total_storage_bytes=1000,
            )

    def test_init_negative_total_storage(self):
        """Test that negative total storage raises error"""
        # Act & Assert
        with pytest.raises(ValueError, match="total_storage_bytes must be positive"):
            UploadQuota(
                daily_limit=5,
                max_file_size_bytes=1000,
                total_storage_bytes=-100,
            )

    def test_free_tier(self):
        """Test creating free tier quota"""
        # Act
        quota = UploadQuota.free_tier()

        # Assert
        assert quota.daily_limit == 2
        assert quota.max_file_size_bytes == 10 * 1024 * 1024  # 10MB
        assert quota.total_storage_bytes == 1 * 1024 * 1024 * 1024  # 1GB

    def test_premium_tier(self):
        """Test creating premium tier quota"""
        # Act
        quota = UploadQuota.premium_tier()

        # Assert
        assert quota.daily_limit == 999999
        assert quota.max_file_size_bytes == 10 * 1024 * 1024  # 10MB
        assert quota.total_storage_bytes == 10 * 1024 * 1024 * 1024  # 10GB

    def test_from_mb_gb(self):
        """Test creating quota from MB/GB values"""
        # Act
        quota = UploadQuota.from_mb_gb(
            daily_limit=10, max_file_mb=5, total_storage_gb=2
        )

        # Assert
        assert quota.daily_limit == 10
        assert quota.max_file_size_bytes == 5 * 1024 * 1024
        assert quota.total_storage_bytes == 2 * 1024 * 1024 * 1024

    def test_can_upload_file_valid(self):
        """Test can_upload_file with valid file size"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert quota.can_upload_file(5 * 1024 * 1024) is True  # 5MB
        assert quota.can_upload_file(10 * 1024 * 1024) is True  # 10MB

    def test_can_upload_file_too_large(self):
        """Test can_upload_file with file too large"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert quota.can_upload_file(15 * 1024 * 1024) is False  # 15MB

    def test_can_upload_file_zero_size(self):
        """Test can_upload_file with zero size file"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert quota.can_upload_file(0) is False

    def test_can_upload_today_under_limit(self):
        """Test can_upload_today when under limit"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert quota.can_upload_today(0) is True
        assert quota.can_upload_today(1) is True

    def test_can_upload_today_at_limit(self):
        """Test can_upload_today when at limit"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert quota.can_upload_today(2) is False

    def test_can_upload_today_over_limit(self):
        """Test can_upload_today when over limit"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert quota.can_upload_today(5) is False

    def test_has_storage_space_available(self):
        """Test has_storage_space when space available"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert (
            quota.has_storage_space(
                current_usage_bytes=100 * 1024 * 1024,  # 100MB
                new_file_bytes=50 * 1024 * 1024,  # 50MB
            )
            is True
        )

    def test_has_storage_space_at_limit(self):
        """Test has_storage_space when at limit"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert (
            quota.has_storage_space(
                current_usage_bytes=1 * 1024 * 1024 * 1024 - 100,  # Almost 1GB
                new_file_bytes=100,
            )
            is True
        )

    def test_has_storage_space_exceeded(self):
        """Test has_storage_space when exceeded"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert (
            quota.has_storage_space(
                current_usage_bytes=900 * 1024 * 1024,  # 900MB
                new_file_bytes=200 * 1024 * 1024,  # 200MB
            )
            is False
        )

    def test_get_remaining_uploads(self):
        """Test get_remaining_uploads"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        assert quota.get_remaining_uploads(0) == 2
        assert quota.get_remaining_uploads(1) == 1
        assert quota.get_remaining_uploads(2) == 0
        assert quota.get_remaining_uploads(5) == 0  # Can't go negative

    def test_get_remaining_storage_bytes(self):
        """Test get_remaining_storage_bytes"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Assert
        assert quota.get_remaining_storage_bytes(0) == 1 * 1024 * 1024 * 1024
        assert (
            quota.get_remaining_storage_bytes(500 * 1024 * 1024)
            == 524 * 1024 * 1024
        )
        assert quota.get_remaining_storage_bytes(2 * 1024 * 1024 * 1024) == 0

    def test_quota_is_immutable(self):
        """Test that UploadQuota is immutable"""
        # Arrange
        quota = UploadQuota.free_tier()

        # Act & Assert
        with pytest.raises(AttributeError):
            quota.daily_limit = 10


class TestQuotaExceededError:
    """Test QuotaExceededError exception"""

    def test_init(self):
        """Test creating QuotaExceededError"""
        # Act
        error = QuotaExceededError(reason="Daily limit exceeded", limit_type="daily")

        # Assert
        assert error.reason == "Daily limit exceeded"
        assert error.limit_type == "daily"
        assert str(error) == "Daily limit exceeded"

    def test_can_be_raised(self):
        """Test that QuotaExceededError can be raised and caught"""
        # Act & Assert
        with pytest.raises(QuotaExceededError) as exc_info:
            raise QuotaExceededError(reason="Storage full", limit_type="storage")

        assert exc_info.value.reason == "Storage full"
        assert exc_info.value.limit_type == "storage"
