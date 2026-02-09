"""
Comment Repository Implementation

SQLAlchemy implementation of the ICommentRepository interface.
"""

from typing import List
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.domain.entities.comment import Comment
from app.modules.posts.domain.repositories.i_comment_repository import ICommentRepository
from app.modules.posts.infrastructure.database.models.post_comment_model import PostCommentModel


class CommentRepositoryImpl(ICommentRepository):
    """Comment Repository Implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comment: Comment) -> Comment:
        """Create a new comment"""
        model = PostCommentModel(
            id=UUID(comment.id),
            post_id=UUID(comment.post_id),
            user_id=UUID(comment.user_id),
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
        
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        
        return self._to_entity(model)

    async def list_by_post(self, post_id: str, limit: int = 50, offset: int = 0) -> List[Comment]:
        """List comments for a post (latest first)"""
        stmt = (
            select(PostCommentModel)
            .where(PostCommentModel.post_id == UUID(post_id))
            .order_by(desc(PostCommentModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_entity(model) for model in models]

    async def get_by_id(self, comment_id: str) -> Comment | None:
        """Get a comment by ID"""
        stmt = select(PostCommentModel).where(PostCommentModel.id == UUID(comment_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._to_entity(model)

    async def count_by_post(self, post_id: str) -> int:
        """Count total comments for a post"""
        stmt = select(func.count()).select_from(PostCommentModel).where(
            PostCommentModel.post_id == UUID(post_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    def _to_entity(self, model: PostCommentModel) -> Comment:
        """Convert ORM model to domain entity"""
        return Comment(
            id=str(model.id),
            post_id=str(model.post_id),
            user_id=str(model.user_id),
            content=model.content,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
