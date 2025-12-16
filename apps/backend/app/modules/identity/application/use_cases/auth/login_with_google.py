"""
Login with Google Use Case
Application layer - coordinates domain logic
"""
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain.entities.profile import Profile
from app.modules.identity.domain.entities.user import User
from app.modules.identity.domain.repositories.profile_repository import (
    IProfileRepository,
)
from app.modules.identity.domain.repositories.user_repository import IUserRepository
from app.modules.identity.infrastructure.database.models import RefreshTokenModel
from app.modules.identity.infrastructure.external.google_oauth_service import (
    GoogleOAuthService,
)
from app.shared.infrastructure.security.jwt_service import jwt_service


class LoginWithGoogleUseCase:
    """
    Use case for logging in with Google OAuth
    Creates user and profile if they don't exist
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        profile_repo: IProfileRepository,
        google_oauth_service: GoogleOAuthService,
        session: AsyncSession
    ):
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.google_oauth = google_oauth_service
        self.session = session

    async def execute(self, google_token: str) -> Optional[Tuple[str, str, User]]:
        """
        Execute login with Google

        Args:
            google_token: Google ID token or auth code

        Returns:
            Tuple of (access_token, refresh_token, user) or None if authentication fails
        """
        # Verify Google token
        user_info = await self.google_oauth.verify_google_token(google_token)
        if not user_info:
            return None

        google_id = user_info["google_id"]
        email = user_info["email"]

        if not email:
            return None

        # Check if user exists
        user = await self.user_repo.get_by_google_id(google_id)

        if not user:
            # Create new user
            user = User(
                google_id=google_id,
                email=email
            )
            user = await self.user_repo.save(user)

            # Create default profile
            profile = Profile(
                user_id=user.id,
                avatar_url=user_info.get("picture")
            )
            await self.profile_repo.save(profile)

        # Generate JWT tokens
        access_token = jwt_service.create_access_token(user.id, user.email)
        refresh_token, expires_at = jwt_service.create_refresh_token(user.id)

        # Save refresh token to database
        refresh_token_model = RefreshTokenModel(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            revoked=False
        )
        self.session.add(refresh_token_model)
        await self.session.flush()

        return access_token, refresh_token, user
