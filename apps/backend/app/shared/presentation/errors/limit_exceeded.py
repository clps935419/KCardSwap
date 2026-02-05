"""Limit Exceeded Error for Quota Management.

This module provides a specialized exception for quota/limit exceeded scenarios.
"""

from datetime import datetime
from typing import Any, Dict, Optional


class LimitExceededError(Exception):
    """Exception raised when a quota or limit is exceeded.

    This exception provides structured information about:
    - What limit was exceeded (limit_key)
    - The maximum allowed value (limit_value)
    - The current usage (current_value)
    - When the limit resets (reset_at)
    """

    def __init__(
        self,
        limit_key: str,
        limit_value: int | float,
        current_value: int | float,
        reset_at: datetime,
        message: Optional[str] = None,
    ) -> None:
        """Initialize LimitExceededError.

        Args:
            limit_key: Identifier for the limit (e.g., 'posts_per_day', 'media_bytes_per_month')
            limit_value: Maximum allowed value
            current_value: Current usage value
            reset_at: When the limit resets (UTC datetime)
            message: Optional custom error message
        """
        self.limit_key = limit_key
        self.limit_value = limit_value
        self.current_value = current_value
        self.reset_at = reset_at
        self.message = message or f"Limit exceeded for {limit_key}"
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format for API response.

        Returns:
            Dictionary with error details following the POC error format
        """
        return {
            "code": "422_LIMIT_EXCEEDED",
            "message": self.message,
            "limit_key": self.limit_key,
            "limit_value": self.limit_value,
            "current_value": self.current_value,
            "reset_at": self.reset_at.isoformat() if isinstance(self.reset_at, datetime) else self.reset_at,
        }
