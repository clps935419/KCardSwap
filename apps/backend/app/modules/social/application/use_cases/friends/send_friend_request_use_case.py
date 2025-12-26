"""Send Friend Request Use Case"""

import uuid
from datetime import datetime

from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.domain.repositories.i_friendship_repository import (
    FriendshipRepository,
)


class SendFriendRequestUseCase:
    """
    Use case for sending a friend request

    Business Rules:
    - User cannot send friend request to themselves
    - Cannot send request if already friends or pending request exists
    - Cannot send request if user is blocked
    """

    def __init__(self, friendship_repository: FriendshipRepository):
        self.friendship_repository = friendship_repository

    async def execute(self, user_id: str, friend_id: str) -> Friendship:
        """
        Send a friend request

        Args:
            user_id: ID of user sending the request
            friend_id: ID of user receiving the request

        Returns:
            Created Friendship entity

        Raises:
            ValueError: If request is invalid (self-request, already exists, blocked)
        """
        # Validate: cannot send request to self
        if user_id == friend_id:
            raise ValueError("Cannot send friend request to yourself")

        # Check if friendship already exists (any direction)
        existing_friendship = await self.friendship_repository.get_by_users(
            user_id, friend_id
        )

        if existing_friendship:
            if existing_friendship.is_accepted():
                raise ValueError("Users are already friends")
            elif existing_friendship.is_pending():
                raise ValueError("Friend request already pending")
            elif existing_friendship.is_blocked():
                raise ValueError("Cannot send friend request - user is blocked")

        # Check if blocked in reverse direction
        if await self.friendship_repository.is_blocked(user_id, friend_id):
            raise ValueError(
                "Cannot send friend request - you are blocked by this user"
            )

        # Create new friend request
        friendship = Friendship(
            id=str(uuid.uuid4()),
            user_id=user_id,
            friend_id=friend_id,
            status=FriendshipStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        return await self.friendship_repository.create(friendship)
