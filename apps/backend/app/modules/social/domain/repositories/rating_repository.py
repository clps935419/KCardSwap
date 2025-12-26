"""
Rating Repository Interface

Domain layer repository interface - defines contract for rating persistence
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.social.domain.entities.rating import Rating


class RatingRepository(ABC):
    """Repository interface for Rating entity persistence"""

    @abstractmethod
    async def create(self, rating: Rating) -> Rating:
        """Create a new rating"""
        pass

    @abstractmethod
    async def get_by_id(self, rating_id: str) -> Optional[Rating]:
        """Get rating by ID"""
        pass

    @abstractmethod
    async def get_by_trade_id(self, trade_id: str) -> List[Rating]:
        """Get all ratings for a specific trade"""
        pass

    @abstractmethod
    async def get_ratings_for_user(self, user_id: str, limit: int = 50) -> List[Rating]:
        """Get ratings received by a user"""
        pass

    @abstractmethod
    async def get_ratings_by_user(self, user_id: str, limit: int = 50) -> List[Rating]:
        """Get ratings given by a user"""
        pass

    @abstractmethod
    async def get_average_rating(self, user_id: str) -> Optional[float]:
        """Get average rating score for a user"""
        pass

    @abstractmethod
    async def has_user_rated_trade(self, rater_id: str, trade_id: str) -> bool:
        """Check if user has already rated a specific trade"""
        pass

    @abstractmethod
    async def delete(self, rating_id: str) -> None:
        """Delete a rating"""
        pass
