"""
SQLAlchemy Rating Repository Implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.rating import Rating
from app.modules.social.domain.repositories.i_rating_repository import IRatingRepository
from app.modules.social.infrastructure.database.models.rating_model import RatingModel


class RatingRepositoryImpl(IRatingRepository):
    """SQLAlchemy implementation of Rating repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, rating: Rating) -> Rating:
        """Create a new rating"""
        model = RatingModel(
            id=UUID(rating.id) if isinstance(rating.id, str) else rating.id,
            rater_id=UUID(rating.rater_id)
            if isinstance(rating.rater_id, str)
            else rating.rater_id,
            rated_user_id=UUID(rating.rated_user_id)
            if isinstance(rating.rated_user_id, str)
            else rating.rated_user_id,
            trade_id=UUID(rating.trade_id)
            if rating.trade_id and isinstance(rating.trade_id, str)
            else (rating.trade_id if rating.trade_id else None),
            score=rating.score,
            comment=rating.comment,
            created_at=rating.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, rating_id: str) -> Optional[Rating]:
        """Get rating by ID"""
        result = await self.session.execute(
            select(RatingModel).where(RatingModel.id == UUID(rating_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_trade_id(self, trade_id: str) -> List[Rating]:
        """Get all ratings for a specific trade"""
        trade_uuid = UUID(trade_id) if isinstance(trade_id, str) else trade_id

        result = await self.session.execute(
            select(RatingModel)
            .where(RatingModel.trade_id == trade_uuid)
            .order_by(RatingModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_ratings_for_user(self, user_id: str, limit: int = 50) -> List[Rating]:
        """Get ratings received by a user"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        result = await self.session.execute(
            select(RatingModel)
            .where(RatingModel.rated_user_id == user_uuid)
            .order_by(RatingModel.created_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_ratings_by_user(self, user_id: str, limit: int = 50) -> List[Rating]:
        """Get ratings given by a user"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        result = await self.session.execute(
            select(RatingModel)
            .where(RatingModel.rater_id == user_uuid)
            .order_by(RatingModel.created_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_average_rating(self, user_id: str) -> Optional[dict]:
        """
        Get average rating score and count for a user

        Returns:
            dict with 'average' (float) and 'count' (int), or None if no ratings
        """
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        result = await self.session.execute(
            select(func.avg(RatingModel.score), func.count(RatingModel.id)).where(
                RatingModel.rated_user_id == user_uuid
            )
        )
        avg_score, count = result.one()

        # Return None if user has no ratings, otherwise return dict
        if avg_score is None or count == 0:
            return None

        return {"average": float(avg_score), "count": int(count)}

    async def find_by_rated_user(self, user_id: str, limit: int = 50) -> List[Rating]:
        """
        Get ratings received by a user (alias for get_ratings_for_user)

        This method provides compatibility with router expectations
        """
        return await self.get_ratings_for_user(user_id, limit)

    async def has_user_rated_trade(self, rater_id: str, trade_id: str) -> bool:
        """Check if user has already rated a specific trade"""
        rater_uuid = UUID(rater_id) if isinstance(rater_id, str) else rater_id
        trade_uuid = UUID(trade_id) if isinstance(trade_id, str) else trade_id

        result = await self.session.execute(
            select(RatingModel).where(
                and_(
                    RatingModel.rater_id == rater_uuid,
                    RatingModel.trade_id == trade_uuid,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def delete(self, rating_id: str) -> None:
        """Delete a rating"""
        result = await self.session.execute(
            select(RatingModel).where(RatingModel.id == UUID(rating_id))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    @staticmethod
    def _to_entity(model: RatingModel) -> Rating:
        """Convert ORM model to domain entity"""
        return Rating(
            id=str(model.id),
            rater_id=str(model.rater_id),
            rated_user_id=str(model.rated_user_id),
            score=model.score,
            comment=model.comment,
            created_at=model.created_at,
            trade_id=str(model.trade_id) if model.trade_id else None,
        )


# Alias for consistency
RatingRepositoryImpl = RatingRepositoryImpl
