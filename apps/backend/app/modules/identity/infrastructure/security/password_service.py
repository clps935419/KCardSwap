"""Password service for admin authentication.

This service provides password hashing and verification for admin users.
"""

from app.shared.infrastructure.security.password_hasher import password_hasher


class PasswordService:
    """Service for password hashing and verification.

    Uses the shared PasswordHasher for consistent password handling.
    """

    def __init__(self):
        """Initialize password service."""
        self._hasher = password_hasher

    def hash_password(self, password: str) -> str:
        """Hash a plaintext password.

        Args:
            password: Plaintext password to hash

        Returns:
            Hashed password string
        """
        return self._hasher.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plaintext password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        return self._hasher.verify(plain_password, hashed_password)
