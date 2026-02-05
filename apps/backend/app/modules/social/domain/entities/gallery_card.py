"""
GalleryCard domain entity for User Story 2.
Represents a card in a user's personal gallery (展示用途，不含交換狀態).
"""
from datetime import datetime
from typing import Optional
from uuid import UUID


class GalleryCard:
    """
    Domain entity representing a gallery card.

    Gallery cards are display-only items in a user's personal album.
    They do not have trading status (持有/欲交換/已交換).
    """

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        title: str,
        idol_name: str,
        era: Optional[str] = None,
        description: Optional[str] = None,
        media_asset_id: Optional[UUID] = None,
        display_order: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.idol_name = idol_name
        self.era = era
        self.description = description
        self.media_asset_id = media_asset_id
        self.display_order = display_order
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_order(self, new_order: int) -> None:
        """Update the display order of this card."""
        self.display_order = new_order
        self.updated_at = datetime.utcnow()

    def attach_media(self, media_asset_id: UUID) -> None:
        """Attach a media asset to this card."""
        self.media_asset_id = media_asset_id
        self.updated_at = datetime.utcnow()

    def update_details(
        self,
        title: Optional[str] = None,
        idol_name: Optional[str] = None,
        era: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update card details."""
        if title is not None:
            self.title = title
        if idol_name is not None:
            self.idol_name = idol_name
        if era is not None:
            self.era = era
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<GalleryCard(id={self.id}, user_id={self.user_id}, title={self.title})>"
