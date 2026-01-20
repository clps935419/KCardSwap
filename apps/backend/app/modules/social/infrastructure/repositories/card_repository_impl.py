"""
SQLAlchemy Card Repository Implementation
"""

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.repositories.i_card_repository import ICardRepository
from app.modules.social.infrastructure.database.models.card_model import CardModel
from app.modules.social.infrastructure.utils.geolocation import haversine_distance


class CardRepositoryImpl(ICardRepository):
    """SQLAlchemy implementation of Card repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, card: Card) -> Card:
        """Save or update a card"""
        # Check if card exists
        result = await self.session.execute(
            select(CardModel).where(CardModel.id == card.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.owner_id = card.owner_id
            existing.idol = card.idol
            existing.idol_group = card.idol_group
            existing.album = card.album
            existing.version = card.version
            existing.rarity = card.rarity
            existing.status = card.status
            existing.image_url = card.image_url
            existing.size_bytes = card.size_bytes
            existing.upload_status = card.upload_status
            existing.upload_confirmed_at = card.upload_confirmed_at
            existing.updated_at = card.updated_at
            model = existing
        else:
            # Create new
            model = CardModel(
                id=card.id,
                owner_id=card.owner_id,
                idol=card.idol,
                idol_group=card.idol_group,
                album=card.album,
                version=card.version,
                rarity=card.rarity,
                status=card.status,
                image_url=card.image_url,
                size_bytes=card.size_bytes,
                upload_status=card.upload_status,
                upload_confirmed_at=card.upload_confirmed_at,
                created_at=card.created_at,
                updated_at=card.updated_at,
            )
            self.session.add(model)

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, card_id: UUID) -> Optional[Card]:
        """Find a card by ID"""
        result = await self.session.execute(
            select(CardModel).where(CardModel.id == card_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_owner(self, owner_id: UUID) -> List[Card]:
        """Find all cards owned by a user"""
        result = await self.session.execute(
            select(CardModel)
            .where(CardModel.owner_id == owner_id)
            .order_by(CardModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def delete(self, card_id: UUID) -> bool:
        """Delete a card by ID"""
        result = await self.session.execute(
            select(CardModel).where(CardModel.id == card_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

    async def count_uploads_today(self, owner_id: UUID) -> int:
        """Count uploads today (since 00:00 UTC)"""
        # Calculate start of day in UTC
        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        result = await self.session.execute(
            select(func.count(CardModel.id)).where(
                and_(
                    CardModel.owner_id == owner_id,
                    CardModel.created_at >= today_start,
                )
            )
        )
        count = result.scalar_one()
        return count or 0

    async def get_total_storage_used(self, owner_id: UUID) -> int:
        """Calculate total storage used by user's cards"""
        result = await self.session.execute(
            select(func.coalesce(func.sum(CardModel.size_bytes), 0)).where(
                CardModel.owner_id == owner_id
            )
        )
        total = result.scalar_one()
        return total or 0

    async def find_by_status(self, owner_id: UUID, status: str) -> List[Card]:
        """Find cards by owner and status"""
        result = await self.session.execute(
            select(CardModel)
            .where(
                and_(
                    CardModel.owner_id == owner_id,
                    CardModel.status == status,
                )
            )
            .order_by(CardModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

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

        This method:
        1. Joins cards with profiles to get owner location and nickname
        2. Filters out users in stealth mode (if requested)
        3. Filters out users without location set
        4. Calculates distance using Haversine formula
        5. Filters by radius
        6. Sorts by distance (closest first)

        Returns list of (Card, distance_km, owner_nickname) tuples
        """
        from app.modules.identity.infrastructure.database.models.profile_model import (
            ProfileModel,
        )

        # Build query: join cards with profiles
        query = (
            select(CardModel, ProfileModel)
            .join(ProfileModel, CardModel.owner_id == ProfileModel.user_id)
            .where(
                and_(
                    CardModel.owner_id != exclude_user_id,  # Exclude searcher
                    CardModel.status == Card.STATUS_AVAILABLE,  # Only available cards
                    ProfileModel.last_lat.isnot(None),  # Must have location
                    ProfileModel.last_lng.isnot(None),
                )
            )
        )

        # Optionally exclude stealth mode users
        if exclude_stealth_users:
            query = query.where(ProfileModel.stealth_mode.is_(False))

        # Execute query
        result = await self.session.execute(query)
        rows = result.all()

        # Calculate distances and filter by radius
        nearby_results: List[Tuple[Card, float, Optional[str]]] = []

        for card_model, profile_model in rows:
            # Calculate distance using Haversine formula
            distance = haversine_distance(
                lat, lng, profile_model.last_lat, profile_model.last_lng
            )

            # Filter by radius
            if distance <= radius_km:
                card = self._to_entity(card_model)
                nearby_results.append((card, distance, profile_model.nickname))

        # Sort by distance (closest first)
        nearby_results.sort(key=lambda x: x[1])

        return nearby_results

    @staticmethod
    def _to_entity(model: CardModel) -> Card:
        """Convert ORM model to domain entity"""
        return Card(
            id=model.id,
            owner_id=model.owner_id,
            idol=model.idol,
            idol_group=model.idol_group,
            album=model.album,
            version=model.version,
            rarity=model.rarity,
            status=model.status,
            image_url=model.image_url,
            size_bytes=model.size_bytes,
            upload_status=getattr(model, "upload_status", "pending"),
            upload_confirmed_at=getattr(model, "upload_confirmed_at", None),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Alias for consistency
CardRepositoryImpl = CardRepositoryImpl
