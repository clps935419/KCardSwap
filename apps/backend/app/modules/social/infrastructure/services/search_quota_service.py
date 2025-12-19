"""
Search quota service for tracking daily search limits.

This service tracks the number of searches performed by users each day
to enforce rate limits (e.g., 5 searches/day for free users).
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Date, Integer, select, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.infrastructure.database.connection import Base


class SearchQuotaModel(Base):
    """ORM model for tracking daily search counts."""

    __tablename__ = "search_quotas"

    user_id = Column(
        PGUUID(as_uuid=True), primary_key=True, nullable=False, index=True
    )
    date = Column(Date, primary_key=True, nullable=False, index=True)
    count = Column(Integer, nullable=False, default=0)


class SearchQuotaService:
    """Service for managing search quota tracking."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the search quota service.

        Args:
            session: Database session for queries
        """
        self.session = session

    async def get_today_count(self, user_id: UUID) -> int:
        """
        Get the number of searches performed by user today.

        Args:
            user_id: User's UUID

        Returns:
            Number of searches performed today (0 if no record exists)
        """
        today = datetime.now(timezone.utc).date()

        stmt = select(SearchQuotaModel.count).where(
            SearchQuotaModel.user_id == user_id, SearchQuotaModel.date == today
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one_or_none()

        return count if count is not None else 0

    async def increment_count(self, user_id: UUID) -> int:
        """
        Increment search count for user today.

        Args:
            user_id: User's UUID

        Returns:
            New count after increment
        """
        today = datetime.now(timezone.utc).date()

        # Try to get existing record
        stmt = select(SearchQuotaModel).where(
            SearchQuotaModel.user_id == user_id, SearchQuotaModel.date == today
        )
        result = await self.session.execute(stmt)
        quota = result.scalar_one_or_none()

        if quota:
            # Increment existing record
            quota.count += 1
            new_count = quota.count
        else:
            # Create new record
            quota = SearchQuotaModel(user_id=user_id, date=today, count=1)
            self.session.add(quota)
            new_count = 1

        await self.session.commit()
        return new_count

    async def check_quota_available(
        self, user_id: UUID, daily_limit: int, is_premium: bool = False
    ) -> tuple[bool, int]:
        """
        Check if user has quota available for search.

        Args:
            user_id: User's UUID
            daily_limit: Daily search limit for free users
            is_premium: Whether user is premium (unlimited searches)

        Returns:
            Tuple of (quota_available: bool, current_count: int)
        """
        if is_premium:
            # Premium users have unlimited searches
            return True, 0

        current_count = await self.get_today_count(user_id)
        quota_available = current_count < daily_limit

        return quota_available, current_count
