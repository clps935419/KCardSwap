"""
Login with Google Use Case - GoogleLoginUseCase
Application layer - coordinates domain logic
Follows DDD: Uses domain entities and repository interfaces
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple

from app.modules.identity.domain.entities.profile import Profile
from app.modules.identity.domain.entities.refresh_token import RefreshToken
from app.modules.identity.domain.entities.user import User
from app.modules.identity.domain.repositories.profile_repository import IProfileRepository
from app.modules.identity.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.modules.identity.domain.repositories.user_repository import IUserRepository
from app.modules.identity.infrastructure.external.google_oauth_service import GoogleOAuthService
from app.shared.infrastructure.security.jwt_service import JWTService


class GoogleLoginUseCase:
    """
    Use case for logging in with Google OAuth
    - Verifies Google ID token
    - Creates or retrieves user
    - Creates profile if new user
    - Generates JWT tokens (access + refresh)
    - Saves refresh token to database
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        profile_repo: IProfileRepository,
        refresh_token_repo: RefreshTokenRepository,
        google_oauth_service: GoogleOAuthService,
        jwt_service: JWTService
    ):
        self._user_repo = user_repo
        self._profile_repo = profile_repo
        self._refresh_token_repo = refresh_token_repo
        self._google_oauth = google_oauth_service
        self._jwt_service = jwt_service

    async def execute(self, google_token: str) -> Optional[Tuple[str, str, User]]:
        """
        Execute Google login flow

        Args:
            google_token: Google ID token

        Returns:
            Tuple of (access_token, refresh_token_string, user) or None if authentication fails
        """
        # Step 1: Verify Google token
        user_info = await self._google_oauth.verify_google_token(google_token)
        if not user_info:
            return None

        google_id = user_info.get("google_id")
        email = user_info.get("email")

        if not email or not google_id:
            return None

        # Step 2: Check if user exists, or create new user
        user = await self._user_repo.get_by_google_id(google_id)

        if not user:
            # Create new user entity
            user = User(
                google_id=google_id,
                email=email
            )
            user = await self._user_repo.save(user)

            # Create default profile for new user
            profile = Profile(
                user_id=user.id,
                avatar_url=user_info.get("picture")
            )
            await self._profile_repo.save(profile)

        # Step 3: Generate JWT tokens
        access_token = self._jwt_service.create_access_token(
            subject=str(user.id),
            additional_claims={"email": user.email}
        )
        
        refresh_token_string = self._jwt_service.create_refresh_token(
            subject=str(user.id),
            additional_claims={"email": user.email}
        )

        # Step 4: Create and save refresh token entity
        expires_at = datetime.utcnow() + timedelta(days=7)  # TODO: use config
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_string,
            expires_at=expires_at,
            revoked=False
        )
        await self._refresh_token_repo.create(refresh_token)

        return access_token, refresh_token_string, user


# Alias for backward compatibility
LoginWithGoogleUseCase = GoogleLoginUseCase
