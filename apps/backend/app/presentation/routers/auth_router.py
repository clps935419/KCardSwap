"""
Auth Router - Authentication endpoints
POST /api/v1/auth/google - Login with Google
POST /api/v1/auth/refresh - Refresh access token
POST /api/v1/auth/logout - Logout (revoke refresh token)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...infrastructure.database.connection import get_db_session
from ...infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ...infrastructure.repositories.sqlalchemy_profile_repository import SQLAlchemyProfileRepository
from ...infrastructure.external.google_oauth_service import GoogleOAuthService
from ...infrastructure.security.jwt_service import JWTService
from ...application.use_cases.auth import LoginWithGoogleUseCase, RefreshTokenUseCase, LogoutUseCase
from ..schemas import GoogleLoginRequest, TokenResponse, RefreshTokenRequest, APIResponse, ErrorDetail
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/google", response_model=APIResponse)
async def login_with_google(
    request: GoogleLoginRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Login with Google OAuth
    
    Exchange Google ID token for JWT access and refresh tokens.
    Creates user and profile if they don't exist.
    """
    # Initialize dependencies
    user_repo = SQLAlchemyUserRepository(session)
    profile_repo = SQLAlchemyProfileRepository(session)
    google_oauth = GoogleOAuthService()
    jwt_service = JWTService()
    
    # Execute use case
    use_case = LoginWithGoogleUseCase(
        user_repo=user_repo,
        profile_repo=profile_repo,
        google_oauth_service=google_oauth,
        jwt_service=jwt_service,
        session=session
    )
    
    result = await use_case.execute(request.google_token)
    
    if not result:
        return APIResponse(
            data=None,
            error=ErrorDetail(
                code="UNAUTHORIZED",
                message="Invalid Google token"
            ).dict()
        )
    
    access_token, refresh_token, user = result
    
    return APIResponse(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=900
        ).dict(),
        error=None
    )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Refresh access token
    
    Exchange refresh token for new access and refresh tokens.
    """
    jwt_service = JWTService()
    use_case = RefreshTokenUseCase(jwt_service=jwt_service, session=session)
    
    result = await use_case.execute(request.refresh_token)
    
    if not result:
        return APIResponse(
            data=None,
            error=ErrorDetail(
                code="UNAUTHORIZED",
                message="Invalid or expired refresh token"
            ).dict()
        )
    
    new_access_token, new_refresh_token = result
    
    return APIResponse(
        data=TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=900
        ).dict(),
        error=None
    )


@router.post("/logout", response_model=APIResponse)
async def logout(
    request: RefreshTokenRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Logout user
    
    Revoke refresh token to logout user.
    Requires valid access token.
    """
    use_case = LogoutUseCase(session=session)
    success = await use_case.execute(user_id, request.refresh_token)
    
    if not success:
        return APIResponse(
            data=None,
            error=ErrorDetail(
                code="BAD_REQUEST",
                message="Invalid refresh token"
            ).dict()
        )
    
    return APIResponse(
        data={"message": "Logged out successfully"},
        error=None
    )
