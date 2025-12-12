"""
Auth Router - Authentication endpoints
POST /api/v1/auth/google - Login with Google
POST /api/v1/auth/refresh - Refresh access token
POST /api/v1/auth/logout - Logout (revoke refresh token)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...domain.repositories.user_repository_interface import IUserRepository
from ...domain.repositories.profile_repository_interface import IProfileRepository
from ...infrastructure.external.google_oauth_service import GoogleOAuthService
from ...infrastructure.security.jwt_service import JWTService
from ...infrastructure.database.connection import get_db_session
from ...application.use_cases.auth import LoginWithGoogleUseCase, RefreshTokenUseCase, LogoutUseCase
from ..schemas import GoogleLoginRequest, TokenResponse, RefreshTokenRequest, APIResponse, ErrorDetail
from ..dependencies import get_current_user_id
from ..dependencies.ioc_dependencies import (
    get_user_repository,
    get_profile_repository,
    get_google_oauth_service,
    get_jwt_service
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/google", response_model=APIResponse)
async def login_with_google(
    request: GoogleLoginRequest,
    session: AsyncSession = Depends(get_db_session),
    user_repo: IUserRepository = Depends(get_user_repository),
    profile_repo: IProfileRepository = Depends(get_profile_repository),
    google_oauth: GoogleOAuthService = Depends(get_google_oauth_service),
    jwt_service: JWTService = Depends(get_jwt_service)
):
    """
    Login with Google OAuth
    
    Exchange Google ID token for JWT access and refresh tokens.
    Creates user and profile if they don't exist.
    """
    # Execute use case with injected dependencies
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
    session: AsyncSession = Depends(get_db_session),
    jwt_service: JWTService = Depends(get_jwt_service)
):
    """
    Refresh access token
    
    Exchange refresh token for new access and refresh tokens.
    """
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
