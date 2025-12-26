"""
ICardRepository Interface - Repository abstraction for Card entities
Following DDD principles: Domain layer defines interface, infrastructure implements
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from app.modules.social.domain.entities.card import Card


class ICardRepository(ABC):
    """
    Repository interface for Card aggregate.
    Defines all persistence operations for cards.
    """

    @abstractmethod
    async def save(self, card: Card) -> Card:
        """
        Save a card (create or update).

        Args:
            card: Card entity to save

        Returns:
            Saved card with updated timestamps
        """
        pass

    @abstractmethod
    async def find_by_id(self, card_id: UUID) -> Optional[Card]:
        """
        Find a card by its ID.

        Args:
            card_id: Card UUID

        Returns:
            Card if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_owner(self, owner_id: UUID) -> List[Card]:
        """
        Find all cards owned by a user.

        Args:
            owner_id: Owner's user ID

        Returns:
            List of cards (empty if none found)
        """
        pass

    @abstractmethod
    async def delete(self, card_id: UUID) -> bool:
        """
        Delete a card by ID.

        Args:
            card_id: Card UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def count_uploads_today(self, owner_id: UUID) -> int:
        """
        Count how many cards a user uploaded today (since 00:00 UTC).

        Args:
            owner_id: Owner's user ID

        Returns:
            Number of uploads today
        """
        pass

    @abstractmethod
    async def get_total_storage_used(self, owner_id: UUID) -> int:
        """
        Calculate total storage used by a user's cards.

        Args:
            owner_id: Owner's user ID

        Returns:
            Total bytes used
        """
        pass

    @abstractmethod
    async def find_by_status(self, owner_id: UUID, status: str) -> List[Card]:
        """
        Find cards by owner and status.

        Args:
            owner_id: Owner's user ID
            status: Card status to filter by

        Returns:
            List of matching cards
        """
        pass

    @abstractmethod
    async def find_nearby_cards(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        exclude_user_id: UUID,
        exclude_stealth_users: bool = True,
    ) -> List[Tuple[Card, float, Optional[str]]]:
        """
        Find cards within a radius from a location.

        Args:
            lat: Latitude of search origin
            lng: Longitude of search origin
            radius_km: Search radius in kilometers
            exclude_user_id: User ID to exclude from results (the searcher)
            exclude_stealth_users: Whether to exclude users in stealth mode

        Returns:
            List of tuples (Card, distance_km, owner_nickname)
            Sorted by distance (closest first)
        """
        pass
