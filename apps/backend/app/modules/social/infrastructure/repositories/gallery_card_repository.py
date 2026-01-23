"""
SQLAlchemy implementation of GalleryCard repository.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.gallery_card import GalleryCard
from app.modules.social.domain.repositories.i_gallery_card_repository import (
    IGalleryCardRepository,
)
from app.modules.social.infrastructure.models.gallery_card_model import GalleryCardModel


class GalleryCardRepository(IGalleryCardRepository):
    """SQLAlchemy implementation of IGalleryCardRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, gallery_card: GalleryCard) -> GalleryCard:
        """Create a new gallery card."""
        model = GalleryCardModel(
            id=gallery_card.id,
            user_id=gallery_card.user_id,
            title=gallery_card.title,
            idol_name=gallery_card.idol_name,
            era=gallery_card.era,
            description=gallery_card.description,
            media_asset_id=gallery_card.media_asset_id,
            display_order=gallery_card.display_order,
            created_at=gallery_card.created_at,
            updated_at=gallery_card.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, card_id: UUID) -> Optional[GalleryCard]:
        """Find a gallery card by ID."""
        stmt = select(GalleryCardModel).where(GalleryCardModel.id == card_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_user_id(
        self, user_id: UUID, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[GalleryCard]:
        """Find all gallery cards for a user, ordered by display_order."""
        stmt = (
            select(GalleryCardModel)
            .where(GalleryCardModel.user_id == user_id)
            .order_by(GalleryCardModel.display_order, GalleryCardModel.created_at)
        )
        
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
            
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, gallery_card: GalleryCard) -> GalleryCard:
        """Update an existing gallery card."""
        stmt = select(GalleryCardModel).where(GalleryCardModel.id == gallery_card.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"GalleryCard with id {gallery_card.id} not found")
        
        model.title = gallery_card.title
        model.idol_name = gallery_card.idol_name
        model.era = gallery_card.era
        model.description = gallery_card.description
        model.media_asset_id = gallery_card.media_asset_id
        model.display_order = gallery_card.display_order
        model.updated_at = gallery_card.updated_at
        
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, card_id: UUID) -> bool:
        """Delete a gallery card. Returns True if deleted, False if not found."""
        stmt = select(GalleryCardModel).where(GalleryCardModel.id == card_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self._session.delete(model)
        await self._session.flush()
        return True

    async def count_by_user_id(self, user_id: UUID) -> int:
        """Count total gallery cards for a user."""
        stmt = select(func.count()).select_from(GalleryCardModel).where(
            GalleryCardModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    def _to_entity(model: GalleryCardModel) -> GalleryCard:
        """Convert SQLAlchemy model to domain entity."""
        return GalleryCard(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            idol_name=model.idol_name,
            era=model.era,
            description=model.description,
            media_asset_id=model.media_asset_id,
            display_order=model.display_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
