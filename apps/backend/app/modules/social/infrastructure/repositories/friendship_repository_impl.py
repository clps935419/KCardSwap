"""
SQLAlchemy Friendship Repository Implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.domain.repositories.friendship_repository import (
    FriendshipRepository,
)
from app.modules.social.infrastructure.database.models.friendship_model import (
    FriendshipModel,
)


class SQLAlchemyFriendshipRepository(FriendshipRepository):
    """SQLAlchemy implementation of Friendship repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, friendship: Friendship) -> Friendship:
        """Create a new friendship record"""
        model = FriendshipModel(
            id=UUID(friendship.id) if isinstance(friendship.id, str) else friendship.id,
            user_id=UUID(friendship.user_id)
            if isinstance(friendship.user_id, str)
            else friendship.user_id,
            friend_id=UUID(friendship.friend_id)
            if isinstance(friendship.friend_id, str)
            else friendship.friend_id,
            status=friendship.status.value
            if isinstance(friendship.status, FriendshipStatus)
            else friendship.status,
            created_at=friendship.created_at,
            updated_at=friendship.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, friendship_id: str) -> Optional[Friendship]:
        """Get friendship by ID"""
        result = await self.session.execute(
            select(FriendshipModel).where(FriendshipModel.id == UUID(friendship_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_users(self, user_id: str, friend_id: str) -> Optional[Friendship]:
        """Get friendship between two users (either direction)"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        friend_uuid = UUID(friend_id) if isinstance(friend_id, str) else friend_id

        result = await self.session.execute(
            select(FriendshipModel).where(
                or_(
                    and_(
                        FriendshipModel.user_id == user_uuid,
                        FriendshipModel.friend_id == friend_uuid,
                    ),
                    and_(
                        FriendshipModel.user_id == friend_uuid,
                        FriendshipModel.friend_id == user_uuid,
                    ),
                )
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_friends_by_user_id(
        self, user_id: str, status: Optional[FriendshipStatus] = None
    ) -> List[Friendship]:
        """Get all friendships for a user, optionally filtered by status"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        query = select(FriendshipModel).where(
            or_(
                FriendshipModel.user_id == user_uuid,
                FriendshipModel.friend_id == user_uuid,
            )
        )

        if status:
            status_value = (
                status.value if isinstance(status, FriendshipStatus) else status
            )
            query = query.where(FriendshipModel.status == status_value)

        query = query.order_by(FriendshipModel.created_at.desc())

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, friendship: Friendship) -> Friendship:
        """Update an existing friendship"""
        result = await self.session.execute(
            select(FriendshipModel).where(
                FriendshipModel.id
                == (
                    UUID(friendship.id)
                    if isinstance(friendship.id, str)
                    else friendship.id
                )
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Friendship with id {friendship.id} not found")

        model.status = (
            friendship.status.value
            if isinstance(friendship.status, FriendshipStatus)
            else friendship.status
        )
        model.updated_at = friendship.updated_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, friendship_id: str) -> None:
        """Delete a friendship"""
        result = await self.session.execute(
            select(FriendshipModel).where(FriendshipModel.id == UUID(friendship_id))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def is_blocked(self, user_id: str, potential_blocker_id: str) -> bool:
        """Check if user is blocked by another user"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        blocker_uuid = (
            UUID(potential_blocker_id)
            if isinstance(potential_blocker_id, str)
            else potential_blocker_id
        )

        result = await self.session.execute(
            select(FriendshipModel).where(
                and_(
                    FriendshipModel.user_id == blocker_uuid,
                    FriendshipModel.friend_id == user_uuid,
                    FriendshipModel.status == FriendshipStatus.BLOCKED.value,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def are_friends(self, user_id: str, other_user_id: str) -> bool:
        """Check if two users are friends (accepted status)"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        other_uuid = (
            UUID(other_user_id) if isinstance(other_user_id, str) else other_user_id
        )

        result = await self.session.execute(
            select(FriendshipModel).where(
                and_(
                    or_(
                        and_(
                            FriendshipModel.user_id == user_uuid,
                            FriendshipModel.friend_id == other_uuid,
                        ),
                        and_(
                            FriendshipModel.user_id == other_uuid,
                            FriendshipModel.friend_id == user_uuid,
                        ),
                    ),
                    FriendshipModel.status == FriendshipStatus.ACCEPTED.value,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_entity(model: FriendshipModel) -> Friendship:
        """Convert ORM model to domain entity"""
        return Friendship(
            id=str(model.id),
            user_id=str(model.user_id),
            friend_id=str(model.friend_id),
            status=FriendshipStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Alias for consistency
FriendshipRepositoryImpl = SQLAlchemyFriendshipRepository
