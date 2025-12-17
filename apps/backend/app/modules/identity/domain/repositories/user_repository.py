"""
User Repository Interface - Repository pattern for User aggregate
"""

from typing import Optional, Protocol
from uuid import UUID

from ..entities.user import User


class IUserRepository(Protocol):
    """
    User repository interface (Protocol/ABC)
    Implementation will be in Infrastructure layer
    """

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        ...

    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        ...

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        ...

    async def save(self, user: User) -> User:
        """Save or update user"""
        ...

    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        ...
