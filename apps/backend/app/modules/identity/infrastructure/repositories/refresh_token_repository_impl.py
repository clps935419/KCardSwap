"""
IRefreshTokenRepository Implementation using SQLAlchemy
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain.entities.refresh_token import RefreshToken
from app.modules.identity.domain.repositories.i_refresh_token_repository import (
    IRefreshTokenRepository,
)
from app.modules.identity.infrastructure.database.models.refresh_token_model import (
    RefreshTokenModel,
)


class RefreshTokenRepositoryImpl(IRefreshTokenRepository):
    """SQLAlchemy implementation of IRefreshTokenRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Create a new refresh token."""
        model = RefreshTokenModel(
            id=refresh_token.id,
            user_id=refresh_token.user_id,
            token=refresh_token.token,
            expires_at=refresh_token.expires_at,
            revoked=refresh_token.revoked,
            created_at=refresh_token.created_at,
            updated_at=refresh_token.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_entity(model)

    async def find_by_token(self, token: str) -> Optional[RefreshToken]:
        """Find refresh token by token string."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def find_by_user_id(self, user_id: UUID) -> list[RefreshToken]:
        """Find all refresh tokens for a user."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def update(self, refresh_token: RefreshToken) -> RefreshToken:
        """Update an existing refresh token."""
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == refresh_token.id)
            .values(revoked=refresh_token.revoked, updated_at=refresh_token.updated_at)
            .execution_options(synchronize_session="fetch")
        )

        await self._session.execute(stmt)
        await self._session.flush()

        # Fetch updated model
        updated_model = await self._session.get(RefreshTokenModel, refresh_token.id)
        if updated_model is None:
            raise ValueError(f"RefreshToken with id {refresh_token.id} not found")

        return self._model_to_entity(updated_model)

    async def delete(self, token_id: UUID) -> bool:
        """Delete a refresh token by ID."""
        model = await self._session.get(RefreshTokenModel, token_id)
        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user."""
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(not RefreshTokenModel.revoked)
            .values(revoked=True)
            .execution_options(synchronize_session="fetch")
        )

        result = await self._session.execute(stmt)
        await self._session.flush()

        return result.rowcount

    async def revoke_token(self, user_id: UUID, token: str) -> bool:
        """Revoke a specific refresh token for a user."""
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token == token,
            RefreshTokenModel.user_id == user_id,
            RefreshTokenModel.revoked == False,
        )
        result = await self._session.execute(stmt)
        token_model = result.scalar_one_or_none()

        if token_model:
            token_model.revoked = True
            await self._session.flush()
            return True

        return False

    @staticmethod
    def _model_to_entity(model: RefreshTokenModel) -> RefreshToken:
        """Convert ORM model to domain entity."""
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            expires_at=model.expires_at,
            revoked=model.revoked,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
