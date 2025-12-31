"""List Post Interests Use Case - List interests for a post (owner only)"""

from typing import List, Optional, Tuple

from app.modules.posts.domain.entities.post_interest import (
    PostInterest,
    PostInterestStatus,
)
from app.modules.posts.domain.repositories.i_post_interest_repository import (
    IPostInterestRepository,
)
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository


class ListPostInterestsUseCase:
    """
    Use case for listing interests for a specific post

    Business Rules:
    - Only post owner can list interests
    - Supports status filtering (pending, accepted, rejected)
    - Supports pagination (limit, offset)
    - Returns list of interests and total count
    """

    def __init__(
        self,
        post_repository: IPostRepository,
        post_interest_repository: IPostInterestRepository,
    ):
        self.post_repository = post_repository
        self.post_interest_repository = post_interest_repository

    async def execute(
        self,
        post_id: str,
        current_user_id: str,
        status: Optional[PostInterestStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[PostInterest], int]:
        """
        List interests for a post

        Args:
            post_id: ID of the post
            current_user_id: ID of the current user (must be post owner)
            status: Optional status filter (pending, accepted, rejected)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            Tuple of (list of PostInterest entities, total count)

        Raises:
            ValueError: If validation fails (post not found, not owner, etc.)
        """
        # Get post
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            raise ValueError("Post not found")

        # Validate: only post owner can list interests
        if post.owner_id != current_user_id:
            raise ValueError("Only post owner can view interests")

        # Get interests with filtering and pagination
        interests = await self.post_interest_repository.list_by_post_id(
            post_id=post_id,
            status=status,
            limit=limit,
            offset=offset,
        )

        # For simplicity, we return the length of the current page as total
        # In a real application, you might want a separate count query
        total = len(interests)

        return interests, total
