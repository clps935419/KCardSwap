"""
Logout Use Case - Revoke refresh token
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.infrastructure.database.models import RefreshTokenModel


class LogoutUseCase:
    """Use case for logging out (revoking refresh token)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, user_id: UUID, refresh_token: str) -> bool:
        """
        Logout user by revoking refresh token

        Args:
            user_id: User ID
            refresh_token: Refresh token to revoke

        Returns:
            True if successful, False otherwise
        """
        # Find and revoke the refresh token
        result = await self.session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token == refresh_token,
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked is False,
            )
        )
        token_model = result.scalar_one_or_none()

        if token_model:
            token_model.revoked = True
            await self.session.flush()
            return True

        return False
