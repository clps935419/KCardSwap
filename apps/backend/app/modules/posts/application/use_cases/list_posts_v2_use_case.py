"""List Posts V2 Use Case - List posts with global/city filtering and category"""

from dataclasses import dataclass
from typing import List, Optional

from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.entities.post_enums import PostCategory
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository
from app.modules.posts.domain.repositories.i_post_like_repository import (
    IPostLikeRepository,
)


@dataclass
class PostWithLikes:
    """Post with like information"""

    post: Post
    like_count: int
    liked_by_me: bool


class ListPostsV2UseCase:
    """
    Use case for listing posts (V2: supports global/city filtering + like information)

    Business Rules (FR-005):
    - Global view (city_code=None): shows all posts (scope=global + scope=city)
    - City view (city_code provided): shows only posts for that city
    - Only show posts with status=open and not expired
    - Support filtering by category
    - Results ordered by created_at DESC (newest first)
    - Include like_count and liked_by_me for each post
    """

    def __init__(
        self, 
        post_repository: IPostRepository,
        like_repository: IPostLikeRepository,
    ):
        self.post_repository = post_repository
        self.like_repository = like_repository

    async def execute(
        self,
        current_user_id: Optional[str] = None,
        city_code: Optional[str] = None,
        category: Optional[PostCategory] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PostWithLikes]:
        """
        List posts with flexible filtering (V2)

        Args:
            current_user_id: Current user ID (for liked_by_me)
            city_code: Optional city filter (None = global view, includes all posts)
            category: Optional category filter
            limit: Maximum number of results (default 50)
            offset: Pagination offset (default 0)

        Returns:
            List of PostWithLikes
        """
        # Use new list_posts method with flexible filtering
        posts = await self.post_repository.list_posts(
            city_code=city_code,
            category=category,
            status=PostStatus.OPEN,
            limit=limit,
            offset=offset,
        )

        # Filter out expired posts (runtime safety check)
        valid_posts = [post for post in posts if not post.is_expired()]

        # Enrich with like information
        posts_with_likes = []
        for post in valid_posts:
            like_count = await self.like_repository.count_by_post(post.id)
            liked_by_me = False
            if current_user_id:
                existing_like = await self.like_repository.get_by_post_and_user(
                    post.id, current_user_id
                )
                liked_by_me = existing_like is not None
            
            posts_with_likes.append(
                PostWithLikes(
                    post=post,
                    like_count=like_count,
                    liked_by_me=liked_by_me,
                )
            )

        return posts_with_likes
