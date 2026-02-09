"""
Create Post Comment Use Case

Business logic for creating a comment on a post.
"""

import uuid
from datetime import datetime, timezone

from app.modules.posts.domain.entities.comment import Comment
from app.modules.posts.domain.repositories.i_comment_repository import ICommentRepository
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository


class CreatePostCommentUseCase:
    """Use case for creating a comment on a post"""

    def __init__(
        self,
        comment_repository: ICommentRepository,
        post_repository: IPostRepository,
    ):
        self.comment_repository = comment_repository
        self.post_repository = post_repository

    async def execute(self, post_id: str, user_id: str, content: str) -> Comment:
        """
        Create a comment on a post
        
        Args:
            post_id: The ID of the post to comment on
            user_id: The ID of the user creating the comment
            content: The comment content
            
        Returns:
            The created comment
            
        Raises:
            ValueError: If the post doesn't exist or content is invalid
        """
        # Verify the post exists
        post = await self.post_repository.get_by_id(post_id)
        if post is None:
            raise ValueError(f"Post not found: {post_id}")
        
        # Create comment entity
        comment = Comment(
            id=str(uuid.uuid4()),
            post_id=post_id,
            user_id=user_id,
            content=content,
            created_at=datetime.now(timezone.utc),
        )
        
        # Persist the comment
        created_comment = await self.comment_repository.create(comment)
        
        return created_comment
