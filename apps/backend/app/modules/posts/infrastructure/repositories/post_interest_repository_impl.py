"""
SQLAlchemy PostInterest Repository Implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.domain.entities.post_interest import (
    PostInterest,
    PostInterestStatus,
)
from app.modules.posts.domain.repositories.i_post_interest_repository import (
    IPostInterestRepository,
)
from app.modules.posts.infrastructure.database.models.post_interest_model import (
    PostInterestModel,
)


class PostInterestRepositoryImpl(IPostInterestRepository):
    """SQLAlchemy implementation of PostInterest repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, post_interest: PostInterest) -> PostInterest:
        """Create a new post interest"""
        model = PostInterestModel(
            id=UUID(post_interest.id) if isinstance(post_interest.id, str) else post_interest.id,
            post_id=UUID(post_interest.post_id) if isinstance(post_interest.post_id, str) else post_interest.post_id,
            user_id=UUID(post_interest.user_id) if isinstance(post_interest.user_id, str) else post_interest.user_id,
            status=post_interest.status.value if isinstance(post_interest.status, PostInterestStatus) else post_interest.status,
            created_at=post_interest.created_at,
            updated_at=post_interest.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, interest_id: str) -> Optional[PostInterest]:
        """Get post interest by ID"""
        result = await self.session.execute(
            select(PostInterestModel).where(PostInterestModel.id == UUID(interest_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_post_and_user(
        self,
        post_id: str,
        user_id: str
    ) -> Optional[PostInterest]:
        """
        Get post interest by post and user
        Used to check for duplicate interests
        """
        post_uuid = UUID(post_id) if isinstance(post_id, str) else post_id
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        result = await self.session.execute(
            select(PostInterestModel).where(
                and_(
                    PostInterestModel.post_id == post_uuid,
                    PostInterestModel.user_id == user_uuid
                )
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_post_id(
        self,
        post_id: str,
        status: Optional[PostInterestStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PostInterest]:
        """
        List all interests for a specific post
        Optionally filtered by status
        """
        post_uuid = UUID(post_id) if isinstance(post_id, str) else post_id

        query = select(PostInterestModel).where(PostInterestModel.post_id == post_uuid)

        if status:
            status_value = status.value if isinstance(status, PostInterestStatus) else status
            query = query.where(PostInterestModel.status == status_value)

        query = query.order_by(PostInterestModel.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def list_by_user_id(
        self,
        user_id: str,
        status: Optional[PostInterestStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PostInterest]:
        """
        List all interests by a specific user
        Optionally filtered by status
        """
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        query = select(PostInterestModel).where(PostInterestModel.user_id == user_uuid)

        if status:
            status_value = status.value if isinstance(status, PostInterestStatus) else status
            query = query.where(PostInterestModel.status == status_value)

        query = query.order_by(PostInterestModel.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, post_interest: PostInterest) -> PostInterest:
        """Update an existing post interest"""
        result = await self.session.execute(
            select(PostInterestModel).where(
                PostInterestModel.id == (UUID(post_interest.id) if isinstance(post_interest.id, str) else post_interest.id)
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"PostInterest with id {post_interest.id} not found")

        model.status = post_interest.status.value if isinstance(post_interest.status, PostInterestStatus) else post_interest.status
        model.updated_at = post_interest.updated_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, interest_id: str) -> None:
        """Delete a post interest"""
        result = await self.session.execute(
            select(PostInterestModel).where(PostInterestModel.id == UUID(interest_id))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    @staticmethod
    def _to_entity(model: PostInterestModel) -> PostInterest:
        """Convert ORM model to domain entity"""
        return PostInterest(
            id=str(model.id),
            post_id=str(model.post_id),
            user_id=str(model.user_id),
            status=PostInterestStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Alias for consistency
PostInterestRepositoryImpl = PostInterestRepositoryImpl
