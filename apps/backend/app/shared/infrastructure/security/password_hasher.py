"""Password hashing service using bcrypt.

This module provides secure password hashing and verification.
"""

from passlib.context import CryptContext


class PasswordHasher:
    """Service for password hashing and verification using bcrypt.

    Uses passlib with bcrypt for secure password storage.
    """

    def __init__(self) -> None:
        """Initialize password hasher with bcrypt context."""
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        """Hash a plaintext password.

        Args:
            password: Plaintext password

        Returns:
            Hashed password
        """
        return self._pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash.

        Args:
            plain_password: Plaintext password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches hash, False otherwise
        """
        return self._pwd_context.verify(plain_password, hashed_password)

    def needs_update(self, hashed_password: str) -> bool:
        """Check if a hashed password needs to be rehashed.

        Args:
            hashed_password: Hashed password to check

        Returns:
            True if password should be rehashed, False otherwise
        """
        return self._pwd_context.needs_update(hashed_password)


# Global password hasher instance
password_hasher = PasswordHasher()
