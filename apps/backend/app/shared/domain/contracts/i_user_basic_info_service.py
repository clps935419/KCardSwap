"""
User Basic Info Service Interface

Contract for getting basic user information across bounded contexts.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class UserBasicInfo:
    """DTO for basic user information"""

    def __init__(self, user_id: UUID, nickname: str, avatar_url: Optional[str] = None):
        self.user_id = user_id
        self.nickname = nickname
        self.avatar_url = avatar_url


class IUserBasicInfoService(ABC):
    """
    Interface for querying basic user information.
    
    This service provides minimal user data for display purposes
    without exposing the Identity bounded context's internal implementation.
    """

    @abstractmethod
    async def get_user_basic_info(self, user_id: UUID) -> Optional[UserBasicInfo]:
        """
        Get basic user information.
        
        Args:
            user_id: User UUID
            
        Returns:
            UserBasicInfo if user exists, None otherwise
        """
        pass
