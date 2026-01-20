"""
User Basic Info Service Implementation

Implements IUserBasicInfoService from shared contracts.
"""

from typing import Optional
from uuid import UUID

from app.modules.identity.domain.repositories.i_profile_repository import (
    IProfileRepository,
)
from app.shared.domain.contracts.i_user_basic_info_service import (
    IUserBasicInfoService,
    UserBasicInfo,
)


class UserBasicInfoServiceImpl(IUserBasicInfoService):
    """
    Implementation of user basic info service.

    Provides minimal user information for display purposes
    across bounded contexts.
    """

    def __init__(self, profile_repository: IProfileRepository):
        self.profile_repository = profile_repository

    async def get_user_basic_info(self, user_id: UUID) -> Optional[UserBasicInfo]:
        """Get basic user information."""
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            return None

        return UserBasicInfo(
            user_id=profile.user_id,
            nickname=profile.nickname or "Unknown User",
            avatar_url=profile.avatar_url,
        )
