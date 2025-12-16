"""Email Value Object.

This module provides a value object for email addresses with validation.
"""
import re
from typing import Any


class Email:
    """Email value object with validation.

    Ensures email addresses are properly formatted and normalized.
    """

    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    def __init__(self, value: str) -> None:
        """Initialize email value object.

        Args:
            value: Email address string

        Raises:
            ValueError: If email format is invalid
        """
        if not value:
            raise ValueError("Email cannot be empty")

        normalized = value.strip().lower()

        if not self.EMAIL_REGEX.match(normalized):
            raise ValueError(f"Invalid email format: {value}")

        self._value = normalized

    @property
    def value(self) -> str:
        """Get the email address value."""
        return self._value

    def __str__(self) -> str:
        """String representation of email."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of email."""
        return f"Email('{self._value}')"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another email."""
        if not isinstance(other, Email):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash(self._value)
