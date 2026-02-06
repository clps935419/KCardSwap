"""
Google OAuth Callback Use Case - GoogleCallbackUseCase
Application layer - coordinates domain logic for PKCE flow
Follows DDD: Uses domain entities and repository interfaces
Supports Expo AuthSession with Authorization Code Flow + PKCE
"""

from datetime import datetime, timedelta
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


class GoogleCallbackUseCase:
    """
    Use case for handling Google OAuth callback with PKCE
    - Exchanges authorization code + code_verifier for ID token
    - Verifies ID token with Google
    - Creates or retrieves user
    - Creates profile if new user
    - Generates JWT tokens (access + refresh)
    - Saves refresh token to database

    This is the recommended flow for Expo AuthSession (mobile apps)
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

    async def execute(
        self, code: str, code_verifier: str, redirect_uri: Optional[str] = None
    ) -> Optional[Tuple[str, str, User]]:
        """
        Execute Google OAuth callback flow with PKCE

        Args:
            code: Authorization code from Google
            code_verifier: PKCE code verifier
            redirect_uri: Optional redirect URI (must match auth request)

        Returns:
            Tuple of (access_token, refresh_token_string, user) or None if authentication fails
        """
        # Step 1: Exchange authorization code for ID token using PKCE
        id_token = await self._google_oauth.exchange_code_with_pkce(
            code=code, code_verifier=code_verifier, redirect_uri=redirect_uri
        )

        if not id_token:
            return None

        # Step 2: Verify ID token with Google
        user_info = await self._google_oauth.verify_google_token(id_token)
        if not user_info:
            return None

        google_id = user_info.get("google_id")
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")

        if not email or not google_id:
            return None

        # Step 3: Check if user exists, or create new user
        user = await self._user_repo.get_by_google_id(google_id)

        if not user:
            # Create new user entity
            user = User(email=email, google_id=google_id)
            user = await self._user_repo.save(user)

            # Create default profile for new user
            profile = Profile(
                user_id=user.id,
                nickname=name,
                avatar_url=picture,
            )
            await self._profile_repo.save(profile)
        else:
            profile = await self._profile_repo.get_by_user_id(user.id)
            if profile:
                nickname_to_set = name if not profile.nickname and name else None
                avatar_to_set = picture if not profile.avatar_url and picture else None
                if nickname_to_set or avatar_to_set:
                    profile.update_profile(
                        nickname=nickname_to_set,
                        avatar_url=avatar_to_set,
                    )
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
