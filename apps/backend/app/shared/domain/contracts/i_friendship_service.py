"""
Friendship Service Interface

Contract for managing friendships across bounded contexts.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


class FriendshipStatusDTO(str, Enum):
    """Friendship status enum for cross-context communication"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class FriendshipDTO:
    """DTO for friendship information"""

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        friend_id: UUID,
        status: FriendshipStatusDTO,
        created_at: datetime,
    ):
        self.id = id
        self.user_id = user_id
        self.friend_id = friend_id
        self.status = status
        self.created_at = created_at


class IFriendshipService(ABC):
    """
    Interface for managing friendships.

    This service provides friendship management functionality
    without exposing the Social bounded context's internal implementation.
    """

    @abstractmethod
    async def get_friendship(
        self, user_id: UUID, friend_id: UUID
    ) -> Optional[FriendshipDTO]:
        """
        Get friendship between two users.

        Args:
            user_id: First user UUID
            friend_id: Second user UUID

        Returns:
            FriendshipDTO if friendship exists, None otherwise
        """
        pass

    @abstractmethod
    async def are_friends(self, user_id: UUID, friend_id: UUID) -> bool:
        """
        Check if two users are friends (accepted status).

        Args:
            user_id: First user UUID
            friend_id: Second user UUID

        Returns:
            True if users are friends, False otherwise
        """
        pass

    @abstractmethod
    async def create_friendship(
        self, user_id: UUID, friend_id: UUID, auto_accept: bool = False
    ) -> FriendshipDTO:
        """
        Create a new friendship or friend request.

        Args:
            user_id: Requesting user UUID
            friend_id: Target user UUID
            auto_accept: If True, automatically accept the friendship

        Returns:
            Created FriendshipDTO
        """
        pass
