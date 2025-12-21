"""
SQLAlchemy Rating Repository Implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.rating import Rating
from app.modules.social.domain.repositories.rating_repository import RatingRepository
from app.modules.social.infrastructure.database.models.rating_model import RatingModel


class SQLAlchemyRatingRepository(RatingRepository):
    """SQLAlchemy implementation of Rating repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, rating: Rating) -> Rating:
        """Create a new rating"""
        model = RatingModel(
            id=UUID(rating.id) if isinstance(rating.id, str) else rating.id,
            rater_id=UUID(rating.rater_id) if isinstance(rating.rater_id, str) else rating.rater_id,
            rated_user_id=UUID(rating.rated_user_id) if isinstance(rating.rated_user_id, str) else rating.rated_user_id,
            trade_id=UUID(rating.trade_id) if isinstance(rating.trade_id, str) else rating.trade_id,
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

    async def get_average_rating(self, user_id: str) -> Optional[float]:
        """Get average rating score for a user"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        
        result = await self.session.execute(
            select(func.avg(RatingModel.score))
            .where(RatingModel.rated_user_id == user_uuid)
        )
        avg_score = result.scalar_one_or_none()
        
        # Return None if user has no ratings, otherwise return float
        return float(avg_score) if avg_score is not None else None

    async def has_user_rated_trade(self, rater_id: str, trade_id: str) -> bool:
        """Check if user has already rated a specific trade"""
        rater_uuid = UUID(rater_id) if isinstance(rater_id, str) else rater_id
        trade_uuid = UUID(trade_id) if isinstance(trade_id, str) else trade_id
        
        result = await self.session.execute(
            select(RatingModel).where(
                and_(
                    RatingModel.rater_id == rater_uuid,
                    RatingModel.trade_id == trade_uuid
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
            trade_id=str(model.trade_id),
            score=model.score,
            comment=model.comment,
            created_at=model.created_at,
        )


# Alias for consistency
RatingRepositoryImpl = SQLAlchemyRatingRepository
