"""Rate User Use Case"""
import uuid
from datetime import datetime
from typing import Optional

from app.modules.social.domain.entities.rating import Rating
from app.modules.social.domain.repositories.rating_repository import RatingRepository


class RateUserUseCase:
    """
    Use case for rating a user after a trade
    
    Business Rules:
    - Rating must be between 1-5 stars
    - User can only rate once per trade
    - User cannot rate themselves
    - Rating should be given after trade completion (verified by caller)
    """
    
    def __init__(self, rating_repository: RatingRepository):
        self.rating_repository = rating_repository
    
    async def execute(
        self,
        rater_id: str,
        rated_user_id: str,
        trade_id: str,
        score: int,
        comment: Optional[str] = None
    ) -> Rating:
        """
        Create a rating for a user after a trade
        
        Args:
            rater_id: ID of user giving the rating
            rated_user_id: ID of user being rated
            trade_id: ID of the trade this rating is for
            score: Rating score (1-5)
            comment: Optional comment (max 1000 chars)
            
        Returns:
            Created Rating entity
            
        Raises:
            ValueError: If validation fails or duplicate rating
        """
        # Check if user has already rated this trade
        has_rated = await self.rating_repository.has_user_rated_trade(rater_id, trade_id)
        if has_rated:
            raise ValueError("User has already rated this trade")
        
        # Create rating (validation happens in entity)
        rating = Rating(
            id=str(uuid.uuid4()),
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            trade_id=trade_id,
            score=score,
            comment=comment,
            created_at=datetime.utcnow()
        )
        
        return await self.rating_repository.create(rating)
