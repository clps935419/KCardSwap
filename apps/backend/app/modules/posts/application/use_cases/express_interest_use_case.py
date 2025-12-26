"""Express Interest Use Case - Express interest in a post"""
import uuid
from datetime import datetime

from app.modules.posts.domain.entities.post_interest import (
    PostInterest,
    PostInterestStatus,
)
from app.modules.posts.domain.repositories.post_interest_repository import (
    PostInterestRepository,
)
from app.modules.posts.domain.repositories.post_repository import PostRepository


class ExpressInterestUseCase:
    """
    Use case for expressing interest in a post

    Business Rules:
    - User cannot express interest in their own post
    - User cannot express interest twice in the same post
    - Post must be open and not expired
    """

    def __init__(
        self,
        post_repository: PostRepository,
        post_interest_repository: PostInterestRepository,
    ):
        self.post_repository = post_repository
        self.post_interest_repository = post_interest_repository

    async def execute(self, post_id: str, user_id: str) -> PostInterest:
        """
        Express interest in a post

        Args:
            post_id: ID of the post
            user_id: ID of the user expressing interest

        Returns:
            Created PostInterest entity

        Raises:
            ValueError: If validation fails
        """
        # Get post
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            raise ValueError("Post not found")

        # Validate: cannot express interest in own post
        if post.owner_id == user_id:
            raise ValueError("Cannot express interest in your own post")

        # Validate: post must be open and not expired
        if not post.can_accept_interests():
            raise ValueError("This post is no longer accepting interests")

        # Check for existing interest
        existing_interest = await self.post_interest_repository.get_by_post_and_user(
            post_id=post_id, user_id=user_id
        )

        if existing_interest:
            raise ValueError("You have already expressed interest in this post")

        # Create interest
        interest = PostInterest(
            id=str(uuid.uuid4()),
            post_id=post_id,
            user_id=user_id,
            status=PostInterestStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        return await self.post_interest_repository.create(interest)
