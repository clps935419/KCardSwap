"""Block User Use Case"""

import uuid
from datetime import datetime

from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.domain.repositories.friendship_repository import (
    FriendshipRepository,
)


class BlockUserUseCase:
    """
    Use case for blocking a user

    Business Rules:
    - User can block any other user
    - Blocking prevents all future interactions (friend requests, messages, trades)
    - If existing friendship exists, it's converted to blocked status
    - User cannot block themselves
    """

    def __init__(self, friendship_repository: FriendshipRepository):
        self.friendship_repository = friendship_repository

    async def execute(self, blocker_user_id: str, blocked_user_id: str) -> Friendship:
        """
        Block a user

        Args:
            blocker_user_id: ID of user doing the blocking
            blocked_user_id: ID of user being blocked

        Returns:
            Updated or created Friendship entity with blocked status

        Raises:
            ValueError: If trying to block self
        """
        # Validate: cannot block self
        if blocker_user_id == blocked_user_id:
            raise ValueError("Cannot block yourself")

        # Check if friendship relationship exists
        existing_friendship = await self.friendship_repository.get_by_users(
            blocker_user_id, blocked_user_id
        )

        if existing_friendship:
            # Update existing friendship to blocked
            existing_friendship.block()
            return await self.friendship_repository.update(existing_friendship)
        else:
            # Create new blocked relationship
            # Note: blocker_user_id is the initiator who blocks
            friendship = Friendship(
                id=str(uuid.uuid4()),
                user_id=blocker_user_id,
                friend_id=blocked_user_id,
                status=FriendshipStatus.BLOCKED,
                created_at=datetime.utcnow(),
            )
            return await self.friendship_repository.create(friendship)
