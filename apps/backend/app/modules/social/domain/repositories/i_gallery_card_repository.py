"""
Repository interface for GalleryCard entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.social.domain.entities.gallery_card import GalleryCard


class IGalleryCardRepository(ABC):
    """Interface for GalleryCard repository."""

    @abstractmethod
    async def create(self, gallery_card: GalleryCard) -> GalleryCard:
        """Create a new gallery card."""
        pass

    @abstractmethod
    async def find_by_id(self, card_id: UUID) -> Optional[GalleryCard]:
        """Find a gallery card by ID."""
        pass

    @abstractmethod
    async def find_by_user_id(
        self, user_id: UUID, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[GalleryCard]:
        """Find all gallery cards for a user, ordered by display_order."""
        pass

    @abstractmethod
    async def update(self, gallery_card: GalleryCard) -> GalleryCard:
        """Update an existing gallery card."""
        pass

    @abstractmethod
    async def delete(self, card_id: UUID) -> bool:
        """Delete a gallery card. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: UUID) -> int:
        """Count total gallery cards for a user."""
        pass
