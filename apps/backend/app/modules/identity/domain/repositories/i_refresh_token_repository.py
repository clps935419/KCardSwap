"""
RefreshTokenRepository Interface - Data access abstraction for refresh tokens
Following DDD principles: Interface in domain layer, implementation in infrastructure
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.modules.identity.domain.entities.refresh_token import RefreshToken


class IRefreshTokenRepository(ABC):
    """
    Repository interface for RefreshToken entity.
    Defines contract for data access operations.
    """

    @abstractmethod
    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Create a new refresh token.

        Args:
            refresh_token: RefreshToken entity to create

        Returns:
            Created RefreshToken entity
        """
        pass

    @abstractmethod
    async def find_by_token(self, token: str) -> Optional[RefreshToken]:
        """Find refresh token by token string.

        Args:
            token: Token string to search for

        Returns:
            RefreshToken entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> list[RefreshToken]:
        """Find all refresh tokens for a user.

        Args:
            user_id: User ID to search for

        Returns:
            List of RefreshToken entities
        """
        pass

    @abstractmethod
    async def update(self, refresh_token: RefreshToken) -> RefreshToken:
        """Update an existing refresh token.

        Args:
            refresh_token: RefreshToken entity to update

        Returns:
            Updated RefreshToken entity
        """
        pass

    @abstractmethod
    async def delete(self, token_id: UUID) -> bool:
        """Delete a refresh token by ID.

        Args:
            token_id: ID of token to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user.

        Args:
            user_id: User ID

        Returns:
            Number of tokens revoked
        """
        pass

    @abstractmethod
    async def revoke_token(self, user_id: UUID, token: str) -> bool:
        """Revoke a specific refresh token for a user.

        Args:
            user_id: User ID
            token: Token string to revoke

        Returns:
            True if token was revoked, False if not found or already revoked
        """
        pass
