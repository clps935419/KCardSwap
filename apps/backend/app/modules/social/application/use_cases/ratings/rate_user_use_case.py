"""Rate User Use Case"""
import uuid
from datetime import datetime
from typing import Optional

from app.modules.social.domain.entities.rating import Rating
from app.modules.social.domain.repositories.i_friendship_repository import (
    IFriendshipRepository,
)
from app.modules.social.domain.repositories.i_rating_repository import IRatingRepository


class RateUserUseCase:
    """
    Use case for rating a user

    Business Rules (FR-SOCIAL-003A - Phase 6 Basic Rating):
    - Rating must be between 1-5 stars
    - User cannot rate themselves
    - User cannot rate if either party has blocked the other
    - Permission: Must be friends OR provide trade_id (trade validation deferred to Phase 7)

    Phase 7 additions (FR-SOCIAL-003B):
    - If trade_id provided: must be completed trade
    - User can only rate once per completed trade
    """

    def __init__(
        self,
        rating_repository: IRatingRepository,
        friendship_repository: IFriendshipRepository
    ):
        self.rating_repository = rating_repository
        self.friendship_repository = friendship_repository

    async def execute(
        self,
        rater_id: str,
        rated_user_id: str,
        score: int,
        comment: Optional[str] = None,
        trade_id: Optional[str] = None
    ) -> Rating:
        """
        Create a rating for a user

        Args:
            rater_id: ID of user giving the rating
            rated_user_id: ID of user being rated
            score: Rating score (1-5)
            comment: Optional comment (max 1000 chars)
            trade_id: Optional trade ID (for trade-based rating)

        Returns:
            Created Rating entity

        Raises:
            ValueError: If validation fails
        """
        # Check for blocking (FR-SOCIAL-003A)
        is_blocked = await self.friendship_repository.is_blocked(rated_user_id, rater_id)
        is_blocker = await self.friendship_repository.is_blocked(rater_id, rated_user_id)

        if is_blocked or is_blocker:
            raise ValueError("Cannot rate user: one party has blocked the other")

        # Permission check (FR-SOCIAL-003A): Must be friends OR provide trade_id
        are_friends = await self.friendship_repository.are_friends(rater_id, rated_user_id)

        if not are_friends and trade_id is None:
            raise ValueError(
                "Cannot rate user: must be friends or provide a valid trade_id"
            )

        # Check for duplicate rating when trade_id is provided
        if trade_id:
            has_rated = await self.rating_repository.has_user_rated_trade(rater_id, trade_id)
            if has_rated:
                raise ValueError("User has already rated this trade")

            # TODO Phase 7 (FR-SOCIAL-003B): Validate trade is completed and involves both parties
            # This requires ITradeRepository which will be implemented in Phase 7

        # Create rating (validation happens in entity)
        rating = Rating(
            id=str(uuid.uuid4()),
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=score,
            comment=comment,
            created_at=datetime.utcnow(),
            trade_id=trade_id
        )

        return await self.rating_repository.create(rating)
