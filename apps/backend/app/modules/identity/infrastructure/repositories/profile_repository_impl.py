"""
SQLAlchemy Profile Repository Implementation
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain.entities.profile import Profile
from app.modules.identity.domain.repositories.profile_repository import (
    IProfileRepository,
)
from app.modules.identity.infrastructure.database.models import ProfileModel


class SQLAlchemyProfileRepository(IProfileRepository):
    """SQLAlchemy implementation of Profile repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        """Get profile by user ID"""
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, profile: Profile) -> Profile:
        """Save or update profile"""
        # Check if profile exists
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.user_id == profile.user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.nickname = profile.nickname
            existing.avatar_url = profile.avatar_url
            existing.bio = profile.bio
            existing.region = profile.region
            existing.preferences = profile.preferences
            existing.privacy_flags = profile.privacy_flags
            existing.updated_at = profile.updated_at
            model = existing
        else:
            # Create new - let database generate ID
            model = ProfileModel(
                user_id=profile.user_id,
                nickname=profile.nickname,
                avatar_url=profile.avatar_url,
                bio=profile.bio,
                region=profile.region,
                preferences=profile.preferences,
                privacy_flags=profile.privacy_flags,
                created_at=profile.created_at,
                updated_at=profile.updated_at,
            )
            self.session.add(model)

        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete profile"""
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

    @staticmethod
    def _to_entity(model: ProfileModel) -> Profile:
        """Convert ORM model to domain entity"""
        return Profile(
            id=model.id,
            user_id=model.user_id,
            nickname=model.nickname,
            avatar_url=model.avatar_url,
            bio=model.bio,
            region=model.region,
            preferences=model.preferences or {},
            privacy_flags=model.privacy_flags
            or {
                "nearby_visible": True,
                "show_online": True,
                "allow_stranger_chat": True,
            },
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Alias for backward compatibility
ProfileRepositoryImpl = SQLAlchemyProfileRepository
