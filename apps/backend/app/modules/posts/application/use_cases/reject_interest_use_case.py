"""Reject Interest Use Case - Reject an interest in a post"""

from app.modules.posts.domain.repositories.i_post_interest_repository import (
    IPostInterestRepository,
)
from app.modules.posts.domain.repositories.post_repository import IPostRepository


class RejectInterestUseCase:
    """
    Use case for rejecting an interest in a post

    Business Rules:
    - Only post owner can reject interests
    - Interest must be pending
    """

    def __init__(
        self,
        post_repository: IPostRepository,
        post_interest_repository: IPostInterestRepository,
    ):
        self.post_repository = post_repository
        self.post_interest_repository = post_interest_repository

    async def execute(
        self, post_id: str, interest_id: str, current_user_id: str
    ) -> None:
        """
        Reject an interest

        Args:
            post_id: ID of the post
            interest_id: ID of the interest to reject
            current_user_id: ID of the current user (must be post owner)

        Raises:
            ValueError: If validation fails
        """
        # Get post
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            raise ValueError("Post not found")

        # Validate: only post owner can reject
        if post.owner_id != current_user_id:
            raise ValueError("Only post owner can reject interests")

        # Get interest
        interest = await self.post_interest_repository.get_by_id(interest_id)
        if not interest:
            raise ValueError("Interest not found")

        # Validate: interest belongs to this post
        if interest.post_id != post_id:
            raise ValueError("Interest does not belong to this post")

        # Validate: interest must be pending
        if not interest.is_pending():
            raise ValueError(f"Interest is already {interest.status}")

        # Reject the interest
        interest.reject()
        await self.post_interest_repository.update(interest)
