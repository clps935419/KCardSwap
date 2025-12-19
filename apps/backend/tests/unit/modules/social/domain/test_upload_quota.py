"""
Unit tests for UploadQuota Value Object (T086)
Testing quota validation and business logic
"""
import pytest

from app.modules.social.domain.value_objects.upload_quota import UploadQuota, QuotaExceeded


class TestUploadQuotaCreation:
    """Test upload quota creation and validation"""

    def test_quota_creation_with_valid_values(self):
        """Test creating quota with valid values"""
        quota = UploadQuota(
            daily_limit=5,
            max_file_size_bytes=10 * 1024 * 1024,  # 10MB
            total_storage_bytes=1 * 1024 * 1024 * 1024,  # 1GB
        )
        
        assert quota.daily_limit == 5
        assert quota.max_file_size_bytes == 10 * 1024 * 1024
        assert quota.total_storage_bytes == 1 * 1024 * 1024 * 1024

    def test_quota_is_immutable(self):
        """Test that quota is immutable (frozen dataclass)"""
        quota = UploadQuota(
            daily_limit=2,
            max_file_size_bytes=10 * 1024 * 1024,
            total_storage_bytes=1 * 1024 * 1024 * 1024,
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            quota.daily_limit = 10

    def test_quota_validation_negative_daily_limit(self):
        """Test validation fails for negative daily_limit"""
        with pytest.raises(ValueError, match="daily_limit must be non-negative"):
            UploadQuota(
                daily_limit=-1,
                max_file_size_bytes=10 * 1024 * 1024,
                total_storage_bytes=1 * 1024 * 1024 * 1024,
            )

    def test_quota_validation_zero_file_size(self):
        """Test validation fails for zero max_file_size_bytes"""
        with pytest.raises(ValueError, match="max_file_size_bytes must be positive"):
            UploadQuota(
                daily_limit=2,
                max_file_size_bytes=0,
                total_storage_bytes=1 * 1024 * 1024 * 1024,
            )

    def test_quota_validation_negative_file_size(self):
        """Test validation fails for negative max_file_size_bytes"""
        with pytest.raises(ValueError, match="max_file_size_bytes must be positive"):
            UploadQuota(
                daily_limit=2,
                max_file_size_bytes=-100,
                total_storage_bytes=1 * 1024 * 1024 * 1024,
            )

    def test_quota_validation_zero_storage(self):
        """Test validation fails for zero total_storage_bytes"""
        with pytest.raises(ValueError, match="total_storage_bytes must be positive"):
            UploadQuota(
                daily_limit=2,
                max_file_size_bytes=10 * 1024 * 1024,
                total_storage_bytes=0,
            )

    def test_quota_validation_negative_storage(self):
        """Test validation fails for negative total_storage_bytes"""
        with pytest.raises(ValueError, match="total_storage_bytes must be positive"):
            UploadQuota(
                daily_limit=2,
                max_file_size_bytes=10 * 1024 * 1024,
                total_storage_bytes=-1000,
            )


class TestUploadQuotaTiers:
    """Test predefined quota tiers"""

    def test_free_tier_quota(self):
        """Test free tier quota values"""
        quota = UploadQuota.free_tier()
        
        assert quota.daily_limit == 2
        assert quota.max_file_size_bytes == 10 * 1024 * 1024  # 10MB
        assert quota.total_storage_bytes == 1 * 1024 * 1024 * 1024  # 1GB

    def test_premium_tier_quota(self):
        """Test premium tier quota values"""
        quota = UploadQuota.premium_tier()
        
        assert quota.daily_limit == 999999  # Effectively unlimited
        assert quota.max_file_size_bytes == 10 * 1024 * 1024  # 10MB
        assert quota.total_storage_bytes == 10 * 1024 * 1024 * 1024  # 10GB

    def test_from_mb_gb_conversion(self):
        """Test creating quota from MB/GB values"""
        quota = UploadQuota.from_mb_gb(
            daily_limit=5,
            max_file_mb=20,
            total_storage_gb=2,
        )
        
        assert quota.daily_limit == 5
        assert quota.max_file_size_bytes == 20 * 1024 * 1024
        assert quota.total_storage_bytes == 2 * 1024 * 1024 * 1024


class TestFileUploadValidation:
    """Test file upload validation logic"""

    def test_can_upload_file_valid_size(self):
        """Test can_upload_file returns True for valid file size"""
        quota = UploadQuota.free_tier()
        
        # 5MB file - should be OK for 10MB limit
        assert quota.can_upload_file(5 * 1024 * 1024) is True
        
        # Exactly at limit
        assert quota.can_upload_file(10 * 1024 * 1024) is True

    def test_can_upload_file_too_large(self):
        """Test can_upload_file returns False for oversized file"""
        quota = UploadQuota.free_tier()
        
        # 11MB file - exceeds 10MB limit
        assert quota.can_upload_file(11 * 1024 * 1024) is False
        
        # Way over limit
        assert quota.can_upload_file(50 * 1024 * 1024) is False

    def test_can_upload_file_zero_or_negative(self):
        """Test can_upload_file returns False for zero or negative size"""
        quota = UploadQuota.free_tier()
        
        assert quota.can_upload_file(0) is False
        assert quota.can_upload_file(-100) is False


class TestDailyUploadValidation:
    """Test daily upload limit validation"""

    def test_can_upload_today_under_limit(self):
        """Test can_upload_today returns True when under limit"""
        quota = UploadQuota.free_tier()  # daily_limit = 2
        
        assert quota.can_upload_today(0) is True  # 0 uploads
        assert quota.can_upload_today(1) is True  # 1 upload

    def test_can_upload_today_at_limit(self):
        """Test can_upload_today returns False when at limit"""
        quota = UploadQuota.free_tier()  # daily_limit = 2
        
        assert quota.can_upload_today(2) is False  # 2 uploads = at limit

    def test_can_upload_today_over_limit(self):
        """Test can_upload_today returns False when over limit"""
        quota = UploadQuota.free_tier()  # daily_limit = 2
        
        assert quota.can_upload_today(3) is False
        assert quota.can_upload_today(100) is False

    def test_get_remaining_uploads(self):
        """Test get_remaining_uploads calculation"""
        quota = UploadQuota.free_tier()  # daily_limit = 2
        
        assert quota.get_remaining_uploads(0) == 2
        assert quota.get_remaining_uploads(1) == 1
        assert quota.get_remaining_uploads(2) == 0
        assert quota.get_remaining_uploads(3) == 0  # Can't go negative


class TestStorageValidation:
    """Test storage limit validation"""

    def test_has_storage_space_available(self):
        """Test has_storage_space returns True when space available"""
        quota = UploadQuota.free_tier()  # 1GB total
        
        # Current usage: 500MB, new file: 200MB -> Total: 700MB < 1GB
        assert quota.has_storage_space(500 * 1024 * 1024, 200 * 1024 * 1024) is True
        
        # Exactly at limit
        assert quota.has_storage_space(900 * 1024 * 1024, 124 * 1024 * 1024) is True

    def test_has_storage_space_exceeded(self):
        """Test has_storage_space returns False when limit exceeded"""
        quota = UploadQuota.free_tier()  # 1GB total
        
        # Current usage: 900MB, new file: 200MB -> Total: 1100MB > 1GB
        assert quota.has_storage_space(900 * 1024 * 1024, 200 * 1024 * 1024) is False

    def test_get_remaining_storage_bytes(self):
        """Test get_remaining_storage_bytes calculation"""
        quota = UploadQuota.free_tier()  # 1GB total
        
        # No usage
        assert quota.get_remaining_storage_bytes(0) == 1 * 1024 * 1024 * 1024
        
        # 500MB used
        remaining = quota.get_remaining_storage_bytes(500 * 1024 * 1024)
        assert remaining == 524 * 1024 * 1024  # ~500MB remaining
        
        # All used
        assert quota.get_remaining_storage_bytes(1 * 1024 * 1024 * 1024) == 0
        
        # Over limit (shouldn't happen, but handle gracefully)
        assert quota.get_remaining_storage_bytes(2 * 1024 * 1024 * 1024) == 0


class TestQuotaExceededException:
    """Test QuotaExceeded exception"""

    def test_quota_exceeded_creation(self):
        """Test creating QuotaExceeded exception"""
        exc = QuotaExceeded("Daily limit exceeded", limit_type="daily")
        
        assert str(exc) == "Daily limit exceeded"
        assert exc.reason == "Daily limit exceeded"
        assert exc.limit_type == "daily"

    def test_quota_exceeded_limit_types(self):
        """Test different limit types"""
        daily_exc = QuotaExceeded("Daily limit", limit_type="daily")
        storage_exc = QuotaExceeded("Storage limit", limit_type="storage")
        file_exc = QuotaExceeded("File size limit", limit_type="file_size")
        
        assert daily_exc.limit_type == "daily"
        assert storage_exc.limit_type == "storage"
        assert file_exc.limit_type == "file_size"


class TestQuotaBoundaryConditions:
    """Test edge cases and boundary conditions"""

    def test_zero_daily_limit(self):
        """Test quota with zero daily limit (no uploads allowed)"""
        quota = UploadQuota(
            daily_limit=0,
            max_file_size_bytes=10 * 1024 * 1024,
            total_storage_bytes=1 * 1024 * 1024 * 1024,
        )
        
        assert quota.can_upload_today(0) is False
        assert quota.get_remaining_uploads(0) == 0

    def test_huge_daily_limit_premium(self):
        """Test premium tier with effectively unlimited daily uploads"""
        quota = UploadQuota.premium_tier()
        
        assert quota.can_upload_today(0) is True
        assert quota.can_upload_today(100) is True
        assert quota.can_upload_today(10000) is True
        assert quota.get_remaining_uploads(10000) > 0

    def test_file_size_exactly_at_byte_boundary(self):
        """Test file size validation at exact byte boundaries"""
        quota = UploadQuota(
            daily_limit=2,
            max_file_size_bytes=1024,  # Exactly 1KB
            total_storage_bytes=1024 * 1024,
        )
        
        assert quota.can_upload_file(1024) is True  # Exactly at limit
        assert quota.can_upload_file(1023) is True  # Just under
        assert quota.can_upload_file(1025) is False  # Just over

    def test_storage_exactly_at_byte_boundary(self):
        """Test storage validation at exact byte boundaries"""
        quota = UploadQuota(
            daily_limit=2,
            max_file_size_bytes=1024,
            total_storage_bytes=2048,  # Exactly 2KB
        )
        
        assert quota.has_storage_space(1024, 1024) is True  # Exactly at limit
        assert quota.has_storage_space(1024, 1023) is True  # Just under
        assert quota.has_storage_space(1024, 1025) is False  # Just over
