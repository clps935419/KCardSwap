"""Create Post Use Case - Create a new city board post with daily limit check"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)


class CreatePostUseCase:
    """
    Use case for creating a new city board post

    Business Rules:
    - Free users: 2 posts per day
    - Premium users: unlimited posts
    - Posts expire after 14 days by default
    - city_code is required
    - title and content are required
    """

    # Daily post limits
    FREE_USER_DAILY_LIMIT = 2
    DEFAULT_EXPIRY_DAYS = 14

    def __init__(
        self,
        post_repository: IPostRepository,
        subscription_repository: ISubscriptionQueryService,
    ):
        self.post_repository = post_repository
        self.subscription_repository = subscription_repository

    async def execute(
        self,
        owner_id: str,
        city_code: str,
        title: str,
        content: str,
        idol: Optional[str] = None,
        idol_group: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Post:
        """
        Create a new post

        Args:
            owner_id: ID of the user creating the post
            city_code: City code (e.g., 'TPE')
            title: Post title (max 120 chars)
            content: Post content
            idol: Optional idol name for filtering
            idol_group: Optional idol group for filtering
            expires_at: Optional expiry datetime (defaults to now + 14 days)

        Returns:
            Created Post entity

        Raises:
            ValueError: If daily limit exceeded or validation fails
        """
        # Validate required fields
        if not city_code:
            raise ValueError("City code is required")
        if not title or len(title) > 120:
            raise ValueError("Title is required and must be <= 120 characters")
        if not content:
            raise ValueError("Content is required")

        # Check daily post limit for free users
        # Convert owner_id string to UUID for the service call
        user_uuid = UUID(owner_id) if isinstance(owner_id, str) else owner_id
        subscription_info = await self.subscription_repository.get_subscription_info(
            user_uuid
        )
        is_premium = (
            subscription_info
            and subscription_info.is_active
            and subscription_info.plan_type == "premium"
        )

        if not is_premium:
            posts_today = await self.post_repository.count_user_posts_today(owner_id)
            if posts_today >= self.FREE_USER_DAILY_LIMIT:
                raise ValueError(
                    f"Daily post limit reached. Free users can create "
                    f"{self.FREE_USER_DAILY_LIMIT} posts per day."
                )

        # Set default expiry if not provided
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=self.DEFAULT_EXPIRY_DAYS)

        # Validate expiry is in the future
        if expires_at <= datetime.now(timezone.utc):
            raise ValueError("Expiry date must be in the future")

        # Create post entity
        post = Post(
            id=str(uuid.uuid4()),
            owner_id=owner_id,
            city_code=city_code,
            title=title,
            content=content,
            idol=idol,
            idol_group=idol_group,
            status=PostStatus.OPEN,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )

        return await self.post_repository.create(post)
