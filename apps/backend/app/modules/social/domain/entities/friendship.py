"""
Friendship Entity - Represents friend relationships between users

Domain Entity following DDD principles - framework independent
"""
from datetime import datetime
from enum import Enum
from typing import Optional


class FriendshipStatus(str, Enum):
    """Friendship status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class Friendship:
    """
    Friendship Entity

    Represents a friend relationship between two users.
    Includes status tracking for pending requests, accepted friendships, and blocks.
    """

    def __init__(
        self,
        id: str,
        user_id: str,
        friend_id: str,
        status: FriendshipStatus,
        created_at: datetime,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.friend_id = friend_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at or created_at

    def accept(self) -> None:
        """Accept a pending friend request"""
        if self.status != FriendshipStatus.PENDING:
            raise ValueError(f"Cannot accept friendship with status {self.status}")
        self.status = FriendshipStatus.ACCEPTED
        self.updated_at = datetime.utcnow()

    def block(self) -> None:
        """Block a user"""
        self.status = FriendshipStatus.BLOCKED
        self.updated_at = datetime.utcnow()

    def is_pending(self) -> bool:
        """Check if friendship is pending"""
        return self.status == FriendshipStatus.PENDING

    def is_accepted(self) -> bool:
        """Check if friendship is accepted"""
        return self.status == FriendshipStatus.ACCEPTED

    def is_blocked(self) -> bool:
        """Check if user is blocked"""
        return self.status == FriendshipStatus.BLOCKED

    def __repr__(self) -> str:
        return (
            f"Friendship(id={self.id}, user_id={self.user_id}, "
            f"friend_id={self.friend_id}, status={self.status})"
        )
