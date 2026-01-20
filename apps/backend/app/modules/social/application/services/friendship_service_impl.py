"""
Friendship Service Implementation

Implements IFriendshipService from shared contracts.
"""

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.domain.repositories.i_friendship_repository import (
    IFriendshipRepository,
)
from app.shared.domain.contracts.i_friendship_service import (
    FriendshipDTO,
    FriendshipStatusDTO,
    IFriendshipService,
)


class FriendshipServiceImpl(IFriendshipService):
    """
    Implementation of friendship service.

    Provides friendship management functionality for other bounded contexts.
    """

    def __init__(self, friendship_repository: IFriendshipRepository):
        self.friendship_repository = friendship_repository

    def _to_dto(self, friendship: Friendship) -> FriendshipDTO:
        """Convert domain entity to DTO."""
        # Map domain status to DTO status
        status_map = {
            FriendshipStatus.PENDING: FriendshipStatusDTO.PENDING,
            FriendshipStatus.ACCEPTED: FriendshipStatusDTO.ACCEPTED,
            FriendshipStatus.BLOCKED: FriendshipStatusDTO.BLOCKED,
        }

        return FriendshipDTO(
            id=UUID(friendship.id),
            user_id=UUID(friendship.user_id),
            friend_id=UUID(friendship.friend_id),
            status=status_map[friendship.status],
            created_at=friendship.created_at,
        )

    async def get_friendship(
        self, user_id: UUID, friend_id: UUID
    ) -> Optional[FriendshipDTO]:
        """Get friendship between two users."""
        friendship = await self.friendship_repository.get_by_users(
            str(user_id), str(friend_id)
        )
        if not friendship:
            return None
        return self._to_dto(friendship)

    async def are_friends(self, user_id: UUID, friend_id: UUID) -> bool:
        """Check if two users are friends (accepted status)."""
        return await self.friendship_repository.are_friends(
            str(user_id), str(friend_id)
        )

    async def create_friendship(
        self, user_id: UUID, friend_id: UUID, auto_accept: bool = False
    ) -> FriendshipDTO:
        """Create a new friendship or friend request."""
        # Check if friendship already exists
        existing = await self.friendship_repository.get_by_users(
            str(user_id), str(friend_id)
        )
        if existing:
            return self._to_dto(existing)

        # Create new friendship
        status = FriendshipStatus.ACCEPTED if auto_accept else FriendshipStatus.PENDING
        friendship = Friendship(
            id=str(uuid.uuid4()),
            user_id=str(user_id),
            friend_id=str(friend_id),
            status=status,
            created_at=datetime.utcnow(),
        )

        created = await self.friendship_repository.create(friendship)
        return self._to_dto(created)
