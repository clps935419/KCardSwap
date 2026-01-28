"""
Login with Google Code Use Case - GoogleCodeLoginUseCase
Application layer - coordinates domain logic
Follows DDD: Uses domain entities and repository interfaces
Supports Web OAuth with Authorization Code Flow (without PKCE)
"""

from datetime import datetime, timedelta
import logging
from typing import Optional, Tuple

from app.modules.identity.domain.entities.profile import Profile
from app.modules.identity.domain.entities.refresh_token import RefreshToken
from app.modules.identity.domain.entities.user import User
from app.modules.identity.domain.repositories.i_profile_repository import (
    IProfileRepository,
)
from app.modules.identity.domain.repositories.i_refresh_token_repository import (
    IRefreshTokenRepository,
)
from app.modules.identity.domain.repositories.i_user_repository import IUserRepository
from app.modules.identity.infrastructure.external.google_oauth_service import (
    GoogleOAuthService,
)
from app.shared.infrastructure.security.jwt_service import JWTService


class GoogleCodeLoginUseCase:
    """
    Use case for logging in with Google OAuth authorization code (Web flow)
    - Exchanges authorization code for ID token
    - Verifies Google ID token
    - Creates or retrieves user
    - Creates profile if new user
    - Generates JWT tokens (access + refresh)
    - Saves refresh token to database

    This is the recommended flow for Web applications using @react-oauth/google
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        profile_repo: IProfileRepository,
        refresh_token_repo: IRefreshTokenRepository,
        google_oauth_service: GoogleOAuthService,
        jwt_service: JWTService,
    ):
        self._user_repo = user_repo
        self._profile_repo = profile_repo
        self._refresh_token_repo = refresh_token_repo
        self._google_oauth = google_oauth_service
        self._jwt_service = jwt_service
        self._logger = logging.getLogger(__name__)

    async def execute(
        self, code: str, redirect_uri: Optional[str] = None
    ) -> Optional[Tuple[str, str, User]]:
        """
        Execute Google login flow with authorization code

        Args:
            code: Authorization code from Google OAuth
            redirect_uri: Optional redirect URI (must match the one used in auth request)

        Returns:
            Tuple of (access_token, refresh_token_string, user) or None if authentication fails
        """
        # Step 1: Exchange authorization code for ID token
        self._logger.info("Exchanging authorization code for ID token")
        
        # Pass redirect_uri to token exchange for OAuth 2.0 security validation
        id_token = await self._google_oauth.exchange_code_for_token(
            code=code, redirect_uri=redirect_uri
        )

        if not id_token:
            self._logger.warning("Failed to exchange authorization code for ID token")
            return None

        # Step 2: Verify Google ID token
        user_info = await self._google_oauth.verify_google_token(id_token)
        if not user_info:
            self._logger.warning(
                "Google code login failed: token verification returned no user info"
            )
            return None

        google_id = user_info.get("google_id")
        email = user_info.get("email")

        if not email or not google_id:
            self._logger.warning(
                "Google code login failed: missing email or google_id (email=%s, google_id=%s)",
                bool(email),
                bool(google_id),
            )
            return None

        # Step 3: Check if user exists, or create new user
        user = await self._user_repo.get_by_google_id(google_id)

        if not user:
            # Create new user entity
            user = User(email=email, google_id=google_id)
            user = await self._user_repo.save(user)

            # Create default profile for new user
            profile = Profile(user_id=user.id, avatar_url=user_info.get("picture"))
            await self._profile_repo.save(profile)

        # Step 4: Generate JWT tokens
        access_token = self._jwt_service.create_access_token(
            subject=str(user.id), additional_claims={"email": user.email}
        )

        refresh_token_string = self._jwt_service.create_refresh_token(
            subject=str(user.id), additional_claims={"email": user.email}
        )

        # Step 5: Create and save refresh token entity
        expires_at = datetime.utcnow() + timedelta(days=7)  # TODO: use config
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_string,
            expires_at=expires_at,
            revoked=False,
        )
        await self._refresh_token_repo.create(refresh_token)

        return access_token, refresh_token_string, user
