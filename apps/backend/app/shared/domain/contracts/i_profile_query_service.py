"""
Profile Query Service Interface

Contract for querying user profile information across bounded contexts.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class UserLocationInfo:
    """DTO for user location information"""

    def __init__(
        self,
        user_id: UUID,
        nickname: str,
        last_lat: Optional[float] = None,
        last_lng: Optional[float] = None,
        stealth_mode: bool = False,
    ):
        self.user_id = user_id
        self.nickname = nickname
        self.last_lat = last_lat
        self.last_lng = last_lng
        self.stealth_mode = stealth_mode


class UserProfileInfo:
    """DTO for user profile information"""

    def __init__(
        self,
        user_id: UUID,
        nickname: str,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        last_lat: Optional[float] = None,
        last_lng: Optional[float] = None,
        stealth_mode: bool = False,
    ):
        self.user_id = user_id
        self.nickname = nickname
        self.bio = bio
        self.avatar_url = avatar_url
        self.last_lat = last_lat
        self.last_lng = last_lng
        self.stealth_mode = stealth_mode


class IProfileQueryService(ABC):
    """
    Interface for querying user profile information.
    
    This service provides read-only access to profile data
    without exposing the Identity bounded context's internal implementation.
    """

    @abstractmethod
    async def get_user_location(self, user_id: UUID) -> Optional[UserLocationInfo]:
        """
        Get user location and basic info.
        
        Args:
            user_id: User UUID
            
        Returns:
            UserLocationInfo if profile exists, None otherwise
        """
        pass

    @abstractmethod
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfileInfo]:
        """
        Get full user profile information.
        
        Args:
            user_id: User UUID
            
        Returns:
            UserProfileInfo if profile exists, None otherwise
        """
        pass

    @abstractmethod
    async def update_user_location(
        self, user_id: UUID, latitude: float, longitude: float
    ) -> bool:
        """
        Update user's last known location.
        
        Args:
            user_id: User UUID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            True if update successful, False otherwise
        """
        pass
