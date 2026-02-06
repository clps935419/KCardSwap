"""SQLAlchemy Media Repository Implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.media.domain.entities.media_asset import MediaAsset, MediaStatus
from app.modules.media.domain.repositories.i_media_repository import IMediaRepository
from app.modules.media.infrastructure.database.models.media_asset_model import (
    MediaAssetModel,
)


class MediaRepositoryImpl(IMediaRepository):
    """SQLAlchemy implementation of Media repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, media: MediaAsset) -> MediaAsset:
        """Create a new media asset."""
        model = MediaAssetModel(
            id=media.id,
            owner_id=media.owner_id,
            gcs_blob_name=media.gcs_blob_name,
            content_type=media.content_type,
            file_size_bytes=media.file_size_bytes,
            status=media.status.value if isinstance(media.status, MediaStatus) else media.status,
            created_at=media.created_at,
            updated_at=media.updated_at,
            confirmed_at=media.confirmed_at,
            target_type=media.target_type,
            target_id=media.target_id,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, media_id: UUID) -> Optional[MediaAsset]:
        """Get media asset by ID."""
        result = await self.session.execute(
            select(MediaAssetModel).where(MediaAssetModel.id == media_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, media: MediaAsset) -> MediaAsset:
        """Update media asset."""
        result = await self.session.execute(
            select(MediaAssetModel).where(MediaAssetModel.id == media.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Media asset {media.id} not found")

        model.status = media.status.value if isinstance(media.status, MediaStatus) else media.status
        model.updated_at = media.updated_at
        model.confirmed_at = media.confirmed_at
        model.target_type = media.target_type
        model.target_id = media.target_id

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_monthly_bytes_used(self, user_id: UUID, year: int, month: int) -> int:
        """Get total bytes used by user in a given month.

        FR-022: Only count confirmed media for quota.
        """
        result = await self.session.execute(
            select(func.coalesce(func.sum(MediaAssetModel.file_size_bytes), 0))
            .where(
                MediaAssetModel.owner_id == user_id,
                MediaAssetModel.status.in_([MediaStatus.CONFIRMED.value, MediaStatus.ATTACHED.value]),
                extract("year", MediaAssetModel.confirmed_at) == year,
                extract("month", MediaAssetModel.confirmed_at) == month,
            )
        )
        return result.scalar() or 0

    async def get_by_ids(self, media_ids: List[UUID]) -> List[MediaAsset]:
        """Get multiple media assets by IDs."""
        if not media_ids:
            return []

        result = await self.session.execute(
            select(MediaAssetModel).where(MediaAssetModel.id.in_(media_ids))
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_by_target(self, target_type: str, target_id: UUID) -> List[MediaAsset]:
        """Get media assets attached to a specific target."""
        result = await self.session.execute(
            select(MediaAssetModel).where(
                MediaAssetModel.target_type == target_type,
                MediaAssetModel.target_id == target_id,
                MediaAssetModel.status == MediaStatus.ATTACHED.value,
            )
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: MediaAssetModel) -> MediaAsset:
        """Convert ORM model to domain entity."""
        return MediaAsset(
            id=model.id,
            owner_id=model.owner_id,
            gcs_blob_name=model.gcs_blob_name,
            content_type=model.content_type,
            file_size_bytes=model.file_size_bytes,
            status=MediaStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            confirmed_at=model.confirmed_at,
            target_type=model.target_type,
            target_id=model.target_id,
        )
