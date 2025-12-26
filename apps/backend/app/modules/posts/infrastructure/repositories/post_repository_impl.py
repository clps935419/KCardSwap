"""
SQLAlchemy Post Repository Implementation
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository
from app.modules.posts.infrastructure.database.models.post_model import PostModel


class PostRepositoryImpl(IPostRepository):
    """SQLAlchemy implementation of Post repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, post: Post) -> Post:
        """Create a new post"""
        model = PostModel(
            id=UUID(post.id) if isinstance(post.id, str) else post.id,
            owner_id=UUID(post.owner_id) if isinstance(post.owner_id, str) else post.owner_id,
            city_code=post.city_code,
            title=post.title,
            content=post.content,
            idol=post.idol,
            idol_group=post.idol_group,
            status=post.status.value if isinstance(post.status, PostStatus) else post.status,
            expires_at=post.expires_at,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, post_id: str) -> Optional[Post]:
        """Get post by ID"""
        result = await self.session.execute(
            select(PostModel).where(PostModel.id == UUID(post_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_city(
        self,
        city_code: str,
        status: Optional[PostStatus] = None,
        idol: Optional[str] = None,
        idol_group: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Post]:
        """
        List posts for a specific city with optional filters
        """
        query = select(PostModel).where(PostModel.city_code == city_code)

        if status:
            status_value = status.value if isinstance(status, PostStatus) else status
            query = query.where(PostModel.status == status_value)

        if idol:
            query = query.where(PostModel.idol == idol)

        if idol_group:
            query = query.where(PostModel.idol_group == idol_group)

        query = query.order_by(PostModel.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count_user_posts_today(self, user_id: str) -> int:
        """
        Count how many posts a user has created today
        """
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        # Get start of day (UTC)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        result = await self.session.execute(
            select(func.count(PostModel.id)).where(
                and_(
                    PostModel.owner_id == user_uuid,
                    PostModel.created_at >= today_start,
                    PostModel.status != PostStatus.DELETED.value
                )
            )
        )
        return result.scalar() or 0

    async def update(self, post: Post) -> Post:
        """Update an existing post"""
        result = await self.session.execute(
            select(PostModel).where(
                PostModel.id == (UUID(post.id) if isinstance(post.id, str) else post.id)
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Post with id {post.id} not found")

        model.city_code = post.city_code
        model.title = post.title
        model.content = post.content
        model.idol = post.idol
        model.idol_group = post.idol_group
        model.status = post.status.value if isinstance(post.status, PostStatus) else post.status
        model.expires_at = post.expires_at
        model.updated_at = post.updated_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, post_id: str) -> None:
        """Delete a post (hard delete)"""
        result = await self.session.execute(
            select(PostModel).where(PostModel.id == UUID(post_id))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def get_by_owner_id(
        self,
        owner_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Post]:
        """Get posts by owner ID"""
        owner_uuid = UUID(owner_id) if isinstance(owner_id, str) else owner_id

        query = (
            select(PostModel)
            .where(PostModel.owner_id == owner_uuid)
            .order_by(PostModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def mark_expired_posts(self) -> int:
        """
        Mark all open posts that have passed their expiry time as expired
        Returns the number of posts marked as expired
        """
        now = datetime.utcnow()

        # Find all open posts that have expired
        result = await self.session.execute(
            select(PostModel).where(
                and_(
                    PostModel.status == PostStatus.OPEN.value,
                    PostModel.expires_at <= now
                )
            )
        )
        expired_posts = result.scalars().all()

        # Mark them as expired
        count = 0
        for model in expired_posts:
            model.status = PostStatus.EXPIRED.value
            model.updated_at = now
            count += 1

        if count > 0:
            await self.session.flush()

        return count

    @staticmethod
    def _to_entity(model: PostModel) -> Post:
        """Convert ORM model to domain entity"""
        return Post(
            id=str(model.id),
            owner_id=str(model.owner_id),
            city_code=model.city_code,
            title=model.title,
            content=model.content,
            idol=model.idol,
            idol_group=model.idol_group,
            status=PostStatus(model.status),
            expires_at=model.expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Alias for consistency
PostRepositoryImpl = PostRepositoryImpl
