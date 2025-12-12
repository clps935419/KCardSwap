"""
Update Profile Use Case
"""
from typing import Optional, Dict, Any
from uuid import UUID

from ....domain.entities.profile import Profile
from ....domain.repositories.profile_repository_interface import IProfileRepository


class UpdateProfileUseCase:
    """Use case for updating user profile"""
    
    def __init__(self, profile_repo: IProfileRepository):
        self.profile_repo = profile_repo
    
    async def execute(
        self,
        user_id: UUID,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        region: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        privacy_flags: Optional[Dict[str, bool]] = None
    ) -> Optional[Profile]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            nickname: New nickname
            avatar_url: New avatar URL
            bio: New bio
            region: New region
            preferences: New preferences
            privacy_flags: New privacy flags
        
        Returns:
            Updated profile or None if not found
        """
        # Get existing profile
        profile = await self.profile_repo.get_by_user_id(user_id)
        
        if not profile:
            # Create new profile if doesn't exist
            profile = Profile(user_id=user_id)
        
        # Update profile fields
        if any([nickname is not None, avatar_url is not None, bio is not None, 
                region is not None, preferences is not None]):
            profile.update_profile(
                nickname=nickname,
                avatar_url=avatar_url,
                bio=bio,
                region=region,
                preferences=preferences
            )
        
        # Update privacy settings separately
        if privacy_flags is not None:
            profile.update_privacy_settings(privacy_flags)
        
        # Save profile
        return await self.profile_repo.save(profile)
