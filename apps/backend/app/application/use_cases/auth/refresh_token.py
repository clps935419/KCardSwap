"""
Refresh Token Use Case
"""
from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.security.jwt_service import JWTService
from ....infrastructure.database.models import RefreshTokenModel


class RefreshTokenUseCase:
    """Use case for refreshing access token"""
    
    def __init__(self, jwt_service: JWTService, session: AsyncSession):
        self.jwt_service = jwt_service
        self.session = session
    
    async def execute(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        """
        Refresh access token
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Tuple of (new_access_token, new_refresh_token) or None if invalid
        """
        # Verify refresh token
        payload = self.jwt_service.verify_token(refresh_token, token_type="refresh")
        if not payload:
            return None
        
        user_id = UUID(payload["sub"])
        
        # Check if refresh token exists and is not revoked
        result = await self.session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token == refresh_token,
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked == False,
                RefreshTokenModel.expires_at > datetime.utcnow()
            )
        )
        token_model = result.scalar_one_or_none()
        
        if not token_model:
            return None
        
        # Get user email from existing token
        email = payload.get("email", "")
        
        # Generate new tokens
        new_access_token = self.jwt_service.create_access_token(user_id, email)
        new_refresh_token, expires_at = self.jwt_service.create_refresh_token(user_id)
        
        # Revoke old refresh token
        token_model.revoked = True
        
        # Save new refresh token
        new_token_model = RefreshTokenModel(
            user_id=user_id,
            token=new_refresh_token,
            expires_at=expires_at,
            revoked=False
        )
        self.session.add(new_token_model)
        await self.session.flush()
        
        return new_access_token, new_refresh_token
