"""
SQLAlchemy PostLike Repository Implementation
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.domain.entities.post_like import PostLike
from app.modules.posts.domain.repositories.i_post_like_repository import (
    IPostLikeRepository,
)
from app.modules.posts.infrastructure.database.models.post_like_model import (
    PostLikeModel,
)


class PostLikeRepositoryImpl(IPostLikeRepository):
    """SQLAlchemy implementation of PostLike repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, like: PostLike) -> PostLike:
        """Create a new like"""
        model = PostLikeModel(
            id=UUID(like.id) if isinstance(like.id, str) else like.id,
            post_id=UUID(like.post_id) if isinstance(like.post_id, str) else like.post_id,
            user_id=UUID(like.user_id) if isinstance(like.user_id, str) else like.user_id,
            created_at=like.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_post_and_user(
        self, post_id: str, user_id: str
    ) -> Optional[PostLike]:
        """Get a like by post_id and user_id"""
        result = await self.session.execute(
            select(PostLikeModel).where(
                and_(
                    PostLikeModel.post_id == UUID(post_id),
                    PostLikeModel.user_id == UUID(user_id),
                )
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def delete_by_post_and_user(self, post_id: str, user_id: str) -> bool:
        """Delete a like by post_id and user_id. Returns True if deleted."""
        result = await self.session.execute(
            delete(PostLikeModel).where(
                and_(
                    PostLikeModel.post_id == UUID(post_id),
                    PostLikeModel.user_id == UUID(user_id),
                )
            )
        )
        await self.session.flush()
        return result.rowcount > 0

    async def count_by_post(self, post_id: str) -> int:
        """Count total likes for a post"""
        result = await self.session.execute(
            select(func.count(PostLikeModel.id)).where(
                PostLikeModel.post_id == UUID(post_id)
            )
        )
        return result.scalar() or 0

    def _to_entity(self, model: PostLikeModel) -> PostLike:
        """Convert ORM model to domain entity"""
        return PostLike(
            id=str(model.id),
            post_id=str(model.post_id),
            user_id=str(model.user_id),
            created_at=model.created_at,
        )
