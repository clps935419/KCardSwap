"""
SQLAlchemy User Repository Implementation
Implements IUserRepository from domain layer
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain.entities.user import User
from app.modules.identity.domain.repositories.user_repository import IUserRepository
from app.modules.identity.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of User repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.google_id == google_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        """Save or update user"""
        # Check if user exists
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.google_id = user.google_id
            existing.email = user.email
            existing.updated_at = user.updated_at
            model = existing
        else:
            # Create new
            model = UserModel(
                id=user.id,
                google_id=user.google_id,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            self.session.add(model)

        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        """Convert ORM model to domain entity"""
        return User(
            id=model.id,
            google_id=model.google_id,
            email=model.email,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
