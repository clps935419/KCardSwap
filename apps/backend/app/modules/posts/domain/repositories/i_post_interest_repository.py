"""
PostInterest Repository Interface

Domain layer repository interface - defines contract for post interest persistence
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.posts.domain.entities.post_interest import (
    PostInterest,
    PostInterestStatus,
)


class IPostInterestRepository(ABC):
    """Repository interface for PostInterest entity persistence"""

    @abstractmethod
    async def create(self, post_interest: PostInterest) -> PostInterest:
        """Create a new post interest"""
        pass

    @abstractmethod
    async def get_by_id(self, interest_id: str) -> Optional[PostInterest]:
        """Get post interest by ID"""
        pass

    @abstractmethod
    async def get_by_post_and_user(
        self,
        post_id: str,
        user_id: str
    ) -> Optional[PostInterest]:
        """
        Get post interest by post and user
        Used to check for duplicate interests
        """
        pass

    @abstractmethod
    async def list_by_post_id(
        self,
        post_id: str,
        status: Optional[PostInterestStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PostInterest]:
        """
        List all interests for a specific post
        Optionally filtered by status
        """
        pass

    @abstractmethod
    async def list_by_user_id(
        self,
        user_id: str,
        status: Optional[PostInterestStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PostInterest]:
        """
        List all interests by a specific user
        Optionally filtered by status
        """
        pass

    @abstractmethod
    async def update(self, post_interest: PostInterest) -> PostInterest:
        """Update an existing post interest"""
        pass

    @abstractmethod
    async def delete(self, interest_id: str) -> None:
        """Delete a post interest"""
        pass
