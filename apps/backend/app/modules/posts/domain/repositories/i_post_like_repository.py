"""
PostLike Repository Interface
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.modules.posts.domain.entities.post_like import PostLike


class IPostLikeRepository(ABC):
    """Repository interface for PostLike operations"""

    @abstractmethod
    async def create(self, like: PostLike) -> PostLike:
        """Create a new like"""
        pass

    @abstractmethod
    async def get_by_post_and_user(
        self, post_id: str, user_id: str
    ) -> Optional[PostLike]:
        """Get a like by post_id and user_id"""
        pass

    @abstractmethod
    async def delete_by_post_and_user(self, post_id: str, user_id: str) -> bool:
        """Delete a like by post_id and user_id. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    async def count_by_post(self, post_id: str) -> int:
        """Count total likes for a post"""
        pass
