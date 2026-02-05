"""
Get Post Use Case

Retrieves a single post by ID with like count and current user's like status.
Phase 9: Includes media_asset_ids for image display.
"""

import logging
from typing import Optional
from uuid import UUID

from app.modules.posts.domain.entities.post import Post
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository
from app.modules.posts.infrastructure.repositories.post_like_repository_impl import (
    PostLikeRepositoryImpl,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class GetPostUseCase:
    """Use case for retrieving a single post by ID"""

    def __init__(
        self,
        post_repository: IPostRepository,
        session: AsyncSession,
    ):
        self.post_repository = post_repository
        self.session = session

    async def execute(
        self, post_id: str, current_user_id: Optional[str] = None
    ) -> Optional[Post]:
        """
        Get a single post by ID

        Args:
            post_id: The post ID to retrieve
            current_user_id: Optional current user ID to check like status

        Returns:
            Post entity with additional like information, or None if not found
        """
        # Get post from repository
        post = await self.post_repository.get_by_id(post_id)

        if not post:
            logger.debug(f"Post not found: {post_id}")
            return None

        # Get like count and current user's like status
        like_repo = PostLikeRepositoryImpl(self.session)
        like_count = await like_repo.count_by_post(post_id)

        liked_by_me = False
        if current_user_id:
            like = await like_repo.get_by_post_and_user(post_id, current_user_id)
            liked_by_me = like is not None

        # Add like information to post (stored as attributes, not in entity)
        post._like_count = like_count
        post._liked_by_me = liked_by_me

        logger.info(
            f"Retrieved post {post_id} with {like_count} likes, "
            f"liked_by_me={liked_by_me}"
        )

        return post
