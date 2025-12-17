"""
RefreshToken Entity - JWT refresh token management
Following DDD principles: No framework dependencies, pure business logic
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class RefreshToken:
    """
    RefreshToken entity representing a JWT refresh token.
    Contains token lifecycle management and business logic.
    """

    def __init__(
        self,
        user_id: UUID,
        token: str,
        expires_at: datetime,
        id: Optional[UUID] = None,
        revoked: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = id or uuid4()
        self._user_id = user_id
        self._token = token
        self._expires_at = expires_at
        self._revoked = revoked
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

        self._validate()

    def _validate(self) -> None:
        """Validate refresh token data."""
        if not self._token:
            raise ValueError("Token cannot be empty")

        if not self._user_id:
            raise ValueError("User ID is required")

        if self._expires_at <= self._created_at:
            raise ValueError("Expiration time must be after creation time")

    # Properties (read-only)
    @property
    def id(self) -> UUID:
        """Get token ID."""
        return self._id

    @property
    def user_id(self) -> UUID:
        """Get user ID."""
        return self._user_id

    @property
    def token(self) -> str:
        """Get token string."""
        return self._token

    @property
    def expires_at(self) -> datetime:
        """Get expiration time."""
        return self._expires_at

    @property
    def revoked(self) -> bool:
        """Check if token is revoked."""
        return self._revoked

    @property
    def created_at(self) -> datetime:
        """Get creation time."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update time."""
        return self._updated_at

    # Business logic methods
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() >= self._expires_at

    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not revoked)."""
        return not self.is_expired() and not self._revoked

    def revoke(self) -> None:
        """Revoke the token."""
        if self._revoked:
            raise ValueError("Token is already revoked")

        self._revoked = True
        self._updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, RefreshToken):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self._id)

    def __repr__(self) -> str:
        """String representation."""
        return f"RefreshToken(id={self._id}, user_id={self._user_id}, expired={self.is_expired()}, revoked={self._revoked})"
