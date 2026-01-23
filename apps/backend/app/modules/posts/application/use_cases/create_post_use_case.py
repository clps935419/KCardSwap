"""Create Post Use Case - Create a new city board post with daily limit check"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from app.modules.posts.application.services.post_quota_service import PostQuotaService
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
        quota_service: Optional[PostQuotaService] = None,
    ):
        self.post_repository = post_repository
        self.subscription_repository = subscription_repository
        # Initialize quota service if not provided (for backward compatibility)
        self.quota_service = quota_service or PostQuotaService(subscription_repository)

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

        # Check daily post limit using quota service
        user_uuid = UUID(owner_id) if isinstance(owner_id, str) else owner_id
        posts_today = await self.post_repository.count_user_posts_today(owner_id)
        
        try:
            await self.quota_service.check_posts_per_day(user_uuid, posts_today)
        except Exception as e:
            # Re-raise LimitExceededException as-is, convert other exceptions to ValueError
            from app.shared.presentation.errors.limit_exceeded import LimitExceededException
            if isinstance(e, LimitExceededException):
                raise
            raise ValueError(str(e))

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
