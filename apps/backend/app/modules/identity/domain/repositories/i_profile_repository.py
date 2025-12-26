"""
Profile Repository Interface
"""

from typing import Optional, Protocol
from uuid import UUID

from ..entities.profile import Profile


class IProfileRepository(Protocol):
    """
    Profile repository interface (Protocol/ABC)
    Implementation will be in Infrastructure layer
    """

    async def get_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        """Get profile by user ID"""
        ...

    async def save(self, profile: Profile) -> Profile:
        """Save or update profile"""
        ...

    async def delete(self, user_id: UUID) -> bool:
        """Delete profile"""
        ...
