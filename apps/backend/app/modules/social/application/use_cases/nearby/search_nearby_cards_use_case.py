"""
Use case for searching nearby cards.
"""

from typing import List

from app.config import settings
from app.modules.social.application.dtos.nearby_dtos import (
    NearbyCardResult,
    SearchNearbyRequest,
)
from app.modules.social.domain.repositories.i_card_repository import ICardRepository
from app.modules.social.infrastructure.services.search_quota_service import (
    SearchQuotaService,
)


class RateLimitExceededException(Exception):  # noqa: N818
    """Exception raised when search rate limit is exceeded."""

    def __init__(self, current_count: int, limit: int):
        self.current_count = current_count
        self.limit = limit
        super().__init__(
            f"Daily search limit exceeded: {current_count}/{limit} searches used"
        )


class SearchNearbyCardsUseCase:
    """
    Use case for searching nearby cards.

    Features:
    - Calculate distance using Haversine formula
    - Filter out stealth mode users
    - Sort by distance (premium users' cards appear first)
    - Track daily search quota (5/day for free, unlimited for premium)
    - Return 429_RATE_LIMIT_EXCEEDED when quota exhausted
    """

    def __init__(
        self,
        card_repository: ICardRepository,
        quota_service: SearchQuotaService,
    ):
        """
        Initialize the use case.

        Args:
            card_repository: Card repository for data access
            quota_service: Service for tracking search quotas
        """
        self.card_repository = card_repository
        self.quota_service = quota_service

    async def execute(
        self, request: SearchNearbyRequest, is_premium: bool = False
    ) -> List[NearbyCardResult]:
        """
        Search for cards near a location.

        Args:
            request: Search request with coordinates and radius
            is_premium: Whether the requesting user is a premium subscriber

        Returns:
            List of nearby cards with distance information, sorted by distance

        Raises:
            RateLimitExceededException: If daily quota exceeded (free users only)
            ValueError: If coordinates or radius are invalid
        """
        # Validate coordinates
        if not -90 <= request.lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= request.lng <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        # Use default radius from config if not provided
        radius_km = request.radius_km or settings.SEARCH_RADIUS_KM
        if radius_km <= 0:
            raise ValueError("Radius must be positive")

        # Check quota (free users only)
        if not is_premium:
            quota_available, current_count = (
                await self.quota_service.check_quota_available(
                    request.user_id, settings.DAILY_SEARCH_LIMIT_FREE, is_premium=False
                )
            )
            if not quota_available:
                raise RateLimitExceededException(
                    current_count, settings.DAILY_SEARCH_LIMIT_FREE
                )

        # Perform search
        results = await self.card_repository.find_nearby_cards(
            lat=request.lat,
            lng=request.lng,
            radius_km=radius_km,
            exclude_user_id=request.user_id,
            exclude_stealth_users=True,
        )

        # Increment quota count (after successful search, free users only)
        if not is_premium:
            await self.quota_service.increment_count(request.user_id)

        # Transform to DTOs
        nearby_cards = [
            NearbyCardResult(
                card_id=card.id,
                owner_id=card.owner_id,
                distance_km=round(distance, 2),  # Round to 2 decimal places
                idol=card.idol,
                idol_group=card.idol_group,
                album=card.album,
                version=card.version,
                rarity=card.rarity,
                image_url=card.image_url,
                owner_nickname=owner_nickname,
            )
            for card, distance, owner_nickname in results
        ]

        return nearby_cards
