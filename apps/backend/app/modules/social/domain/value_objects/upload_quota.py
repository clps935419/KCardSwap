"""
UploadQuota Value Object - Represents upload limitations for users
Following DDD principles: Immutable value object with validation logic
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UploadQuota:
    """
    Value object representing upload quota constraints.
    Immutable and validated upon creation.
    """

    daily_limit: int  # Maximum uploads per day
    max_file_size_bytes: int  # Maximum file size in bytes
    total_storage_bytes: int  # Total storage limit in bytes

    def __post_init__(self):
        """Validate quota values"""
        if self.daily_limit < 0:
            raise ValueError("daily_limit must be non-negative")
        if self.max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be positive")
        if self.total_storage_bytes <= 0:
            raise ValueError("total_storage_bytes must be positive")

    @classmethod
    def free_tier(cls) -> "UploadQuota":
        """
        Create a free tier upload quota.
        - 2 uploads per day
        - 10MB max file size
        - 1GB total storage
        """
        return cls(
            daily_limit=2,
            max_file_size_bytes=10 * 1024 * 1024,  # 10MB
            total_storage_bytes=1 * 1024 * 1024 * 1024,  # 1GB
        )

    @classmethod
    def premium_tier(cls) -> "UploadQuota":
        """
        Create a premium tier upload quota.
        - Unlimited uploads per day (represented as large number)
        - 10MB max file size
        - 10GB total storage
        """
        return cls(
            daily_limit=999999,  # Effectively unlimited
            max_file_size_bytes=10 * 1024 * 1024,  # 10MB
            total_storage_bytes=10 * 1024 * 1024 * 1024,  # 10GB
        )

    @classmethod
    def from_mb_gb(cls, daily_limit: int, max_file_mb: int, total_storage_gb: int) -> "UploadQuota":
        """
        Create quota from MB/GB values for convenience.

        Args:
            daily_limit: Daily upload limit
            max_file_mb: Max file size in MB
            total_storage_gb: Total storage in GB
        """
        return cls(
            daily_limit=daily_limit,
            max_file_size_bytes=max_file_mb * 1024 * 1024,
            total_storage_bytes=total_storage_gb * 1024 * 1024 * 1024,
        )

    def can_upload_file(self, file_size_bytes: int) -> bool:
        """Check if a file of given size can be uploaded"""
        return 0 < file_size_bytes <= self.max_file_size_bytes

    def can_upload_today(self, uploads_today: int) -> bool:
        """Check if user can upload today"""
        return uploads_today < self.daily_limit

    def has_storage_space(self, current_usage_bytes: int, new_file_bytes: int) -> bool:
        """Check if user has enough storage space"""
        return (current_usage_bytes + new_file_bytes) <= self.total_storage_bytes

    def get_remaining_uploads(self, uploads_today: int) -> int:
        """Get remaining uploads for today"""
        remaining = self.daily_limit - uploads_today
        return max(0, remaining)

    def get_remaining_storage_bytes(self, current_usage_bytes: int) -> int:
        """Get remaining storage in bytes"""
        remaining = self.total_storage_bytes - current_usage_bytes
        return max(0, remaining)


class QuotaExceeded(Exception):  # noqa: N818
    """Exception raised when upload quota is exceeded"""

    def __init__(self, reason: str, limit_type: str):
        """
        Args:
            reason: Human-readable reason for quota exceeded
            limit_type: Type of limit exceeded (daily/file_size/storage)
        """
        self.reason = reason
        self.limit_type = limit_type
        super().__init__(reason)
