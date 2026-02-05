"""Media repository interface."""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.modules.media.domain.entities.media_asset import MediaAsset


class IMediaRepository(ABC):
    """Repository interface for MediaAsset operations."""

    @abstractmethod
    async def create(self, media: MediaAsset) -> MediaAsset:
        """Create a new media asset.

        Args:
            media: MediaAsset entity to create

        Returns:
            Created MediaAsset entity
        """
        pass

    @abstractmethod
    async def get_by_id(self, media_id: UUID) -> Optional[MediaAsset]:
        """Get media asset by ID.

        Args:
            media_id: Media ID

        Returns:
            MediaAsset entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def update(self, media: MediaAsset) -> MediaAsset:
        """Update media asset.

        Args:
            media: MediaAsset entity to update

        Returns:
            Updated MediaAsset entity
        """
        pass

    @abstractmethod
    async def get_monthly_bytes_used(self, user_id: UUID, year: int, month: int) -> int:
        """Get total bytes used by user in a given month.

        Args:
            user_id: User ID
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Total bytes used in the month
        """
        pass
