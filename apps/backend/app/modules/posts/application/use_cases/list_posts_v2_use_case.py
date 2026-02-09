"""List Posts V2 Use Case - List posts with global/city filtering and category"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.infrastructure.database.models.profile_model import ProfileModel
from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.entities.post_enums import PostCategory
from app.modules.posts.domain.repositories.i_post_like_repository import (
    IPostLikeRepository,
)
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository


@dataclass
class PostWithLikes:
    """Post with like information"""

    post: Post
    like_count: int
    liked_by_me: bool
    owner_nickname: Optional[str] = None
    owner_avatar_url: Optional[str] = None


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
        session: AsyncSession,
    ):
        self.post_repository = post_repository
        self.like_repository = like_repository
        self.session = session

    async def _fetch_owner_profiles(
        self, owner_ids: List[str]
    ) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Fetch profile information for multiple owners in a single query.
        
        Returns:
            Dict mapping owner_id to {nickname, avatar_url}
        """
        if not owner_ids:
            return {}
        
        # Convert to UUIDs
        uuid_ids = [UUID(owner_id) for owner_id in owner_ids]
        
        # Query profiles
        result = await self.session.execute(
            select(
                ProfileModel.user_id,
                ProfileModel.nickname,
                ProfileModel.avatar_url,
            ).where(ProfileModel.user_id.in_(uuid_ids))
        )
        
        # Build mapping
        profiles = {}
        for row in result:
            user_id_str = str(row[0])
            profiles[user_id_str] = {
                "nickname": row[1],
                "avatar_url": row[2],
            }
        
        return profiles

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

        # Fetch all owner profiles in a single query
        owner_ids = list(set(post.owner_id for post in valid_posts))
        owner_profiles = await self._fetch_owner_profiles(owner_ids)

        # Enrich with like information and owner profiles
        posts_with_likes = []
        for post in valid_posts:
            like_count = await self.like_repository.count_by_post(post.id)
            liked_by_me = False
            if current_user_id:
                existing_like = await self.like_repository.get_by_post_and_user(
                    post.id, current_user_id
                )
                liked_by_me = existing_like is not None

            # Get owner profile info
            profile = owner_profiles.get(post.owner_id, {})
            owner_nickname = profile.get("nickname")
            owner_avatar_url = profile.get("avatar_url")

            posts_with_likes.append(
                PostWithLikes(
                    post=post,
                    like_count=like_count,
                    liked_by_me=liked_by_me,
                    owner_nickname=owner_nickname,
                    owner_avatar_url=owner_avatar_url,
                )
            )

        return posts_with_likes
