"""
Post Repository Interface

Domain layer repository interface - defines contract for post persistence
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.entities.post_enums import PostCategory


class IPostRepository(ABC):
    """Repository interface for Post entity persistence"""

    @abstractmethod
    async def create(self, post: Post) -> Post:
        """Create a new post"""
        pass

    @abstractmethod
    async def get_by_id(self, post_id: str) -> Optional[Post]:
        """Get post by ID"""
        pass

    @abstractmethod
    async def list_by_city(
        self,
        city_code: str,
        status: Optional[PostStatus] = None,
        idol: Optional[str] = None,
        idol_group: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Post]:
        """
        List posts for a specific city with optional filters

        Args:
            city_code: City code (required)
            status: Filter by post status
            idol: Filter by idol name
            idol_group: Filter by idol group
            limit: Maximum number of results
            offset: Pagination offset
        """
        pass

    @abstractmethod
    async def list_posts(
        self,
        city_code: Optional[str] = None,
        category: Optional[PostCategory] = None,
        status: Optional[PostStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Post]:
        """
        List posts with flexible filtering (V2: supports global/city filtering)

        FR-005:
        - When city_code is None: returns all posts (global + city)
        - When city_code is provided: returns only posts with that city_code

        Args:
            city_code: Optional city filter (None = global view, includes all posts)
            category: Optional category filter
            status: Filter by post status (defaults to OPEN)
            limit: Maximum number of results
            offset: Pagination offset
        """
        pass

    @abstractmethod
    async def count_user_posts_today(self, user_id: str) -> int:
        """
        Count how many posts a user has created today
        Used for daily post limit checking
        """
        pass

    @abstractmethod
    async def update(self, post: Post) -> Post:
        """Update an existing post"""
        pass

    @abstractmethod
    async def delete(self, post_id: str) -> None:
        """Delete a post (hard delete)"""
        pass

    @abstractmethod
    async def get_by_owner_id(
        self, owner_id: str, limit: int = 50, offset: int = 0
    ) -> List[Post]:
        """Get posts by owner ID"""
        pass

    @abstractmethod
    async def mark_expired_posts(self) -> int:
        """
        Mark all open posts that have passed their expiry time as expired
        Returns the number of posts marked as expired
        """
        pass
