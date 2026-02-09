"""
Comment Repository Interface

Defines the contract for comment persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List

from app.modules.posts.domain.entities.comment import Comment


class ICommentRepository(ABC):
    """Comment Repository Interface"""

    @abstractmethod
    async def create(self, comment: Comment) -> Comment:
        """Create a new comment"""
        pass

    @abstractmethod
    async def list_by_post(self, post_id: str, limit: int = 50, offset: int = 0) -> List[Comment]:
        """List comments for a post (latest first)"""
        pass

    @abstractmethod
    async def get_by_id(self, comment_id: str) -> Comment | None:
        """Get a comment by ID"""
        pass

    @abstractmethod
    async def count_by_post(self, post_id: str) -> int:
        """Count total comments for a post"""
        pass
