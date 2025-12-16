"""
Refresh Token Use Case
Application layer - coordinates token refresh logic
Follows DDD: Uses domain entities and repository interfaces
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from jose import JWTError

from app.modules.identity.domain.entities.refresh_token import RefreshToken
from app.modules.identity.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.shared.infrastructure.security.jwt_service import JWTService


class RefreshTokenUseCase:
    """Use case for refreshing access token using refresh token"""

    def __init__(
        self,
        refresh_token_repo: RefreshTokenRepository,
        jwt_service: JWTService
    ):
        self._refresh_token_repo = refresh_token_repo
        self._jwt_service = jwt_service

    async def execute(self, refresh_token_string: str) -> Optional[Tuple[str, str]]:
        """
        Refresh access token

        Args:
            refresh_token_string: Refresh token string

        Returns:
            Tuple of (new_access_token, new_refresh_token) or None if invalid
        """
        # Step 1: Verify JWT signature and expiration
        try:
            payload = self._jwt_service.verify_token(refresh_token_string, expected_type="refresh")
        except (JWTError, ValueError):
            return None

        user_id = UUID(payload["sub"])
        email = payload.get("email", "")

        # Step 2: Check if refresh token exists in database and is valid
        token_entity = await self._refresh_token_repo.find_by_token(refresh_token_string)
        
        if not token_entity or not token_entity.is_valid():
            return None

        # Step 3: Revoke old refresh token
        token_entity.revoke()
        await self._refresh_token_repo.update(token_entity)

        # Step 4: Generate new tokens
        new_access_token = self._jwt_service.create_access_token(
            subject=str(user_id),
            additional_claims={"email": email}
        )
        
        new_refresh_token_string = self._jwt_service.create_refresh_token(
            subject=str(user_id),
            additional_claims={"email": email}
        )

        # Step 5: Save new refresh token
        expires_at = datetime.utcnow() + timedelta(days=7)  # TODO: use config
        new_token_entity = RefreshToken(
            user_id=user_id,
            token=new_refresh_token_string,
            expires_at=expires_at,
            revoked=False
        )
        await self._refresh_token_repo.create(new_token_entity)

        return new_access_token, new_refresh_token_string
