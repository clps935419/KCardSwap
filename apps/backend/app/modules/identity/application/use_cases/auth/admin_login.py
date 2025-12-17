"""
Admin Login Use Case - AdminLoginUseCase
Application layer for admin authentication using email/password
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from app.modules.identity.domain.entities.refresh_token import RefreshToken
from app.modules.identity.domain.entities.user import User
from app.modules.identity.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.modules.identity.domain.repositories.user_repository import IUserRepository
from app.modules.identity.infrastructure.security.password_service import (
    PasswordService,
)
from app.shared.infrastructure.security.jwt_service import JWTService


class AdminLoginUseCase:
    """
    Use case for admin login with email/password
    - Verifies email and password
    - Checks if user has admin role
    - Generates JWT tokens (access + refresh)
    - Saves refresh token to database
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        refresh_token_repo: RefreshTokenRepository,
        password_service: PasswordService,
        jwt_service: JWTService,
    ):
        self._user_repo = user_repo
        self._refresh_token_repo = refresh_token_repo
        self._password_service = password_service
        self._jwt_service = jwt_service

    async def execute(
        self, email: str, password: str
    ) -> Optional[Tuple[str, str, User]]:
        """
        Execute admin login flow

        Args:
            email: Admin email address
            password: Admin password

        Returns:
            Tuple of (access_token, refresh_token_string, user) or None if authentication fails
        """
        # Step 1: Get user by email
        user = await self._user_repo.get_by_email(email)
        if not user:
            return None

        # Step 2: Verify user has password_hash (not a Google OAuth user)
        if not user.password_hash:
            return None

        # Step 3: Verify password
        if not self._password_service.verify_password(password, user.password_hash):
            return None

        # Step 4: Check if user has admin role
        if not user.is_admin():
            return None

        # Step 5: Generate JWT tokens
        access_token = self._jwt_service.create_access_token(
            subject=str(user.id),
            additional_claims={"email": user.email, "role": user.role},
        )

        refresh_token_string = self._jwt_service.create_refresh_token(
            subject=str(user.id),
            additional_claims={"email": user.email, "role": user.role},
        )

        # Step 6: Create and save refresh token entity
        expires_at = datetime.utcnow() + timedelta(days=7)
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_string,
            expires_at=expires_at,
            revoked=False,
        )
        await self._refresh_token_repo.create(refresh_token)

        return access_token, refresh_token_string, user
