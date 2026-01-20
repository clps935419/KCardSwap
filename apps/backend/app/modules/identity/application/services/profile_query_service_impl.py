"""
Profile Query Service Implementation

Implements IProfileQueryService from shared contracts.
"""

from typing import Optional
from uuid import UUID

from app.modules.identity.domain.repositories.i_profile_repository import (
    IProfileRepository,
)
from app.shared.domain.contracts.i_profile_query_service import (
    IProfileQueryService,
    UserLocationInfo,
    UserProfileInfo,
)


class ProfileQueryServiceImpl(IProfileQueryService):
    """
    Implementation of profile query service.

    Provides read-only and limited write access to profile information
    for other bounded contexts.
    """

    def __init__(self, profile_repository: IProfileRepository):
        self.profile_repository = profile_repository

    async def get_user_location(self, user_id: UUID) -> Optional[UserLocationInfo]:
        """Get user location and basic info."""
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            return None

        return UserLocationInfo(
            user_id=profile.user_id,
            nickname=profile.nickname or "",
            last_lat=profile.last_lat,
            last_lng=profile.last_lng,
            stealth_mode=profile.stealth_mode,
        )

    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfileInfo]:
        """Get full user profile information."""
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            return None

        return UserProfileInfo(
            user_id=profile.user_id,
            nickname=profile.nickname or "",
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            last_lat=profile.last_lat,
            last_lng=profile.last_lng,
            stealth_mode=profile.stealth_mode,
        )

    async def update_user_location(
        self, user_id: UUID, latitude: float, longitude: float
    ) -> bool:
        """Update user's last known location."""
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            return False

        try:
            profile.update_location(latitude, longitude)
            await self.profile_repository.save(profile)
            return True
        except (ValueError, Exception):
            return False
