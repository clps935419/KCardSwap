"""List Posts V2 Use Case - List posts with global/city filtering and category"""

from typing import List, Optional

from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.entities.post_enums import PostCategory
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository


class ListPostsV2UseCase:
    """
    Use case for listing posts (V2: supports global/city filtering)

    Business Rules (FR-005):
    - Global view (city_code=None): shows all posts (scope=global + scope=city)
    - City view (city_code provided): shows only posts for that city
    - Only show posts with status=open and not expired
    - Support filtering by category
    - Results ordered by created_at DESC (newest first)
    """

    def __init__(self, post_repository: IPostRepository):
        self.post_repository = post_repository

    async def execute(
        self,
        city_code: Optional[str] = None,
        category: Optional[PostCategory] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Post]:
        """
        List posts with flexible filtering (V2)

        Args:
            city_code: Optional city filter (None = global view, includes all posts)
            category: Optional category filter
            limit: Maximum number of results (default 50)
            offset: Pagination offset (default 0)

        Returns:
            List of Post entities
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

        return valid_posts
