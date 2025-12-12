"""
Get Profile Use Case
"""
from typing import Optional
from uuid import UUID

from ....domain.entities.profile import Profile
from ....infrastructure.repositories.sqlalchemy_profile_repository import SQLAlchemyProfileRepository


class GetProfileUseCase:
    """Use case for getting user profile"""
    
    def __init__(self, profile_repo: SQLAlchemyProfileRepository):
        self.profile_repo = profile_repo
    
    async def execute(self, user_id: UUID) -> Optional[Profile]:
        """
        Get user profile
        
        Args:
            user_id: User ID
        
        Returns:
            Profile or None if not found
        """
        return await self.profile_repo.get_by_user_id(user_id)
