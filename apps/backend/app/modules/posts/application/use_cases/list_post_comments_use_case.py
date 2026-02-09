"""
List Post Comments Use Case

Business logic for listing comments on a post.
"""

from typing import List

from app.modules.posts.domain.entities.comment import Comment
from app.modules.posts.domain.repositories.i_comment_repository import ICommentRepository


class ListPostCommentsUseCase:
    """Use case for listing comments on a post"""

    def __init__(self, comment_repository: ICommentRepository):
        self.comment_repository = comment_repository

    async def execute(
        self,
        post_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Comment], int]:
        """
        List comments for a post (latest first)
        
        Args:
            post_id: The ID of the post
            limit: Maximum number of comments to return
            offset: Number of comments to skip
            
        Returns:
            Tuple of (comments list, total count)
        """
        # Get comments and total count
        comments = await self.comment_repository.list_by_post(
            post_id=post_id,
            limit=limit,
            offset=offset,
        )
        
        total = await self.comment_repository.count_by_post(post_id)
        
        return comments, total
