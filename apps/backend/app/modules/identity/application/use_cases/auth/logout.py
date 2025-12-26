"""
Logout Use Case - Revoke refresh token
"""

from uuid import UUID

from app.modules.identity.domain.repositories.i_refresh_token_repository import (
    IRefreshTokenRepository,
)


class LogoutUseCase:
    """Use case for logging out (revoking refresh token)"""

    def __init__(self, refresh_token_repo: IRefreshTokenRepository):
        self.refresh_token_repo = refresh_token_repo

    async def execute(self, user_id: UUID, refresh_token: str) -> bool:
        """
        Logout user by revoking refresh token

        Args:
            user_id: User ID
            refresh_token: Refresh token to revoke

        Returns:
            True if successful, False otherwise
        """
        # Revoke the refresh token using repository
        return await self.refresh_token_repo.revoke_token(user_id, refresh_token)
