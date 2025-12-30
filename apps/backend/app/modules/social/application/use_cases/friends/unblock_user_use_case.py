"""Unblock User Use Case"""

from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.domain.repositories.i_friendship_repository import (
    IFriendshipRepository,
)


class UnblockUserUseCase:
    """
    Use case for unblocking a user

    Business Rules:
    - User can unblock a previously blocked user
    - Unblocking removes the blocked relationship entirely
    - After unblocking, users can interact again (send friend requests, chat)
    - Unblocking does not automatically make them friends
    - User cannot unblock themselves
    - Can only unblock if a blocked relationship exists
    """

    def __init__(self, friendship_repository: IFriendshipRepository):
        self.friendship_repository = friendship_repository

    async def execute(self, unblocker_user_id: str, unblocked_user_id: str) -> None:
        """
        Unblock a user

        Args:
            unblocker_user_id: ID of user doing the unblocking (must be the original blocker)
            unblocked_user_id: ID of user being unblocked

        Returns:
            None (relationship is removed)

        Raises:
            ValueError: If trying to unblock self, or if no blocked relationship exists
        """
        # Validate: cannot unblock self
        if unblocker_user_id == unblocked_user_id:
            raise ValueError("Cannot unblock yourself")

        # Check if blocked relationship exists
        existing_friendship = await self.friendship_repository.get_by_users(
            unblocker_user_id, unblocked_user_id
        )

        if not existing_friendship:
            raise ValueError("No relationship exists with this user")

        # Verify it's a blocked relationship
        if not existing_friendship.is_blocked():
            raise ValueError(
                f"Cannot unblock: relationship status is {existing_friendship.status.value}, not blocked"
            )

        # Verify the current user is the blocker (user_id in the friendship)
        # The blocker is always stored as user_id in the blocked relationship
        if existing_friendship.user_id != unblocker_user_id:
            raise ValueError("You are not the one who blocked this user")

        # Delete the blocked relationship to allow future interactions
        await self.friendship_repository.delete(existing_friendship.id)
