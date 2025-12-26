"""
Friendship Repository Interface

Domain layer repository interface - defines contract for friendship persistence
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus


class FriendshipRepository(ABC):
    """Repository interface for Friendship entity persistence"""

    @abstractmethod
    async def create(self, friendship: Friendship) -> Friendship:
        """Create a new friendship record"""
        pass

    @abstractmethod
    async def get_by_id(self, friendship_id: str) -> Optional[Friendship]:
        """Get friendship by ID"""
        pass

    @abstractmethod
    async def get_by_users(self, user_id: str, friend_id: str) -> Optional[Friendship]:
        """Get friendship between two users (either direction)"""
        pass

    @abstractmethod
    async def get_friends_by_user_id(
        self, user_id: str, status: Optional[FriendshipStatus] = None
    ) -> List[Friendship]:
        """Get all friendships for a user, optionally filtered by status"""
        pass

    @abstractmethod
    async def update(self, friendship: Friendship) -> Friendship:
        """Update an existing friendship"""
        pass

    @abstractmethod
    async def delete(self, friendship_id: str) -> None:
        """Delete a friendship"""
        pass

    @abstractmethod
    async def is_blocked(self, user_id: str, potential_blocker_id: str) -> bool:
        """Check if user is blocked by another user"""
        pass

    @abstractmethod
    async def are_friends(self, user_id: str, other_user_id: str) -> bool:
        """Check if two users are friends (accepted status)"""
        pass
