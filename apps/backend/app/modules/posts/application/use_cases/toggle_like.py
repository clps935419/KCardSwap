"""
Toggle Like Use Case
Idempotent like/unlike: if liked, unlike; if not liked, like (FR-008, FR-009)
"""

import logging
from dataclasses import dataclass

from app.modules.posts.domain.entities.post_like import PostLike
from app.modules.posts.domain.repositories.i_post_like_repository import (
    IPostLikeRepository,
)
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository

logger = logging.getLogger(__name__)


@dataclass
class ToggleLikeResult:
    """Result of toggle like operation"""

    liked: bool  # True if now liked, False if unliked
    like_count: int  # Current like count


class ToggleLikeUseCase:
    """
    Use case for toggling like on a post
    
    Implements idempotent toggle pattern:
    - If user has liked the post, unlike it
    - If user has not liked the post, like it
    """

    def __init__(
        self,
        post_repository: IPostRepository,
        like_repository: IPostLikeRepository,
    ):
        self.post_repository = post_repository
        self.like_repository = like_repository

    async def execute(self, post_id: str, user_id: str) -> ToggleLikeResult:
        """
        Toggle like on a post
        
        Args:
            post_id: Post ID to like/unlike
            user_id: User ID performing the action
            
        Returns:
            ToggleLikeResult with liked status and current like count
            
        Raises:
            ValueError: If post not found
        """
        # Verify post exists
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            raise ValueError(f"Post not found: {post_id}")

        # Check if user has already liked the post
        existing_like = await self.like_repository.get_by_post_and_user(
            post_id, user_id
        )

        if existing_like:
            # Unlike: remove the like
            await self.like_repository.delete_by_post_and_user(post_id, user_id)
            liked = False
            logger.info(f"User {user_id} unliked post {post_id}")
        else:
            # Like: create a new like
            new_like = PostLike.create(post_id=post_id, user_id=user_id)
            await self.like_repository.create(new_like)
            liked = True
            logger.info(f"User {user_id} liked post {post_id}")

        # Get updated like count
        like_count = await self.like_repository.count_by_post(post_id)

        return ToggleLikeResult(liked=liked, like_count=like_count)
