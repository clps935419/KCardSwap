"""
Authentication Router for Identity Module
Handles Google login, token refresh, and logout
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.identity.application.use_cases.auth.admin_login import (
    AdminLoginUseCase,
)
from app.modules.identity.application.use_cases.auth.google_callback import (
    GoogleCallbackUseCase,
)
from app.modules.identity.application.use_cases.auth.login_with_google import (
    GoogleLoginUseCase,
)
from app.modules.identity.application.use_cases.auth.refresh_token import (
    RefreshTokenUseCase,
)
from app.modules.identity.domain.repositories.profile_repository import (
    IProfileRepository,
)
from app.modules.identity.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.modules.identity.domain.repositories.user_repository import IUserRepository
from app.modules.identity.infrastructure.external.google_oauth_service import (
    GoogleOAuthService,
)
from app.modules.identity.infrastructure.repositories.profile_repository_impl import (
    ProfileRepositoryImpl,
)
from app.modules.identity.infrastructure.repositories.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from app.modules.identity.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.modules.identity.infrastructure.security.password_service import (
    PasswordService,
)
from app.modules.identity.presentation.schemas.auth_schemas import (
    AdminLoginRequest,
    ErrorWrapper,
    GoogleCallbackRequest,
    GoogleLoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.infrastructure.security.jwt_service import JWTService

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/admin-login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully authenticated as admin"},
        400: {"model": ErrorWrapper, "description": "Validation error"},
        401: {
            "model": ErrorWrapper,
            "description": "Invalid credentials or not an admin",
        },
    },
    tags=["Admin"],
    summary="Admin login with email/password",
    description="Authenticate admin user with email and password. Only users with admin or super_admin role can login.",
)
async def admin_login(
    request: AdminLoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """
    Admin login with email/password.

    - Verifies email and password
    - Checks if user has admin role (admin or super_admin)
    - Returns JWT access and refresh tokens

    This endpoint is only for admin users with password-based authentication.
    Regular users should use Google OAuth login.
    """
    # Initialize dependencies
    user_repo: IUserRepository = UserRepositoryImpl(session)
    refresh_token_repo: RefreshTokenRepository = RefreshTokenRepositoryImpl(session)
    password_service = PasswordService()
    jwt_service = JWTService()

    # Create and execute use case
    use_case = AdminLoginUseCase(
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        password_service=password_service,
        jwt_service=jwt_service,
    )

    result = await use_case.execute(request.email, request.password)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Invalid credentials or not an admin user",
            },
        )

    access_token, refresh_token, user = result

    # Commit transaction
    await session.commit()

    # Build response
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user_id=user.id,
        email=user.email,
        role=user.role,
    )

    return LoginResponse(data=token_response, error=None)


@router.post(
    "/google-login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully authenticated"},
        400: {"model": ErrorWrapper, "description": "Validation error"},
        401: {"model": ErrorWrapper, "description": "Invalid Google token"},
    },
    summary="Login with Google",
    description="Authenticate user with Google OAuth token and receive JWT tokens",
)
async def google_login(
    request: GoogleLoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """
    Login with Google OAuth.

    - Verifies Google ID token
    - Creates user and profile if new user
    - Returns JWT access and refresh tokens
    """
    # Initialize dependencies
    user_repo: IUserRepository = UserRepositoryImpl(session)
    profile_repo: IProfileRepository = ProfileRepositoryImpl(session)
    refresh_token_repo: RefreshTokenRepository = RefreshTokenRepositoryImpl(session)
    google_oauth_service = GoogleOAuthService()
    jwt_service = JWTService()

    # Create and execute use case
    use_case = GoogleLoginUseCase(
        user_repo=user_repo,
        profile_repo=profile_repo,
        refresh_token_repo=refresh_token_repo,
        google_oauth_service=google_oauth_service,
        jwt_service=jwt_service,
    )

    result = await use_case.execute(request.google_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid Google token"},
        )

    access_token, refresh_token, user = result

    # Commit transaction
    await session.commit()

    # Build response
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user_id=user.id,
        email=user.email,
    )

    return LoginResponse(data=token_response, error=None)


@router.post(
    "/google-callback",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully authenticated"},
        400: {"model": ErrorWrapper, "description": "Validation error"},
        401: {
            "model": ErrorWrapper,
            "description": "Invalid authorization code or code_verifier",
        },
        422: {"model": ErrorWrapper, "description": "Token exchange failed"},
    },
    summary="Google OAuth Callback with PKCE",
    description="Authenticate user with Google OAuth authorization code and PKCE code_verifier (Expo AuthSession)",
)
async def google_callback(
    request: GoogleCallbackRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """
    Google OAuth callback with PKCE (Recommended for Expo AuthSession).

    - Exchanges authorization code + code_verifier for ID token
    - Verifies Google ID token
    - Creates user and profile if new user
    - Returns JWT access and refresh tokens

    This endpoint implements Authorization Code Flow with PKCE,
    which is the recommended OAuth flow for mobile applications.
    """
    # Initialize dependencies
    user_repo: IUserRepository = UserRepositoryImpl(session)
    profile_repo: IProfileRepository = ProfileRepositoryImpl(session)
    refresh_token_repo: RefreshTokenRepository = RefreshTokenRepositoryImpl(session)
    google_oauth_service = GoogleOAuthService()
    jwt_service = JWTService()

    # Create and execute use case
    use_case = GoogleCallbackUseCase(
        user_repo=user_repo,
        profile_repo=profile_repo,
        refresh_token_repo=refresh_token_repo,
        google_oauth_service=google_oauth_service,
        jwt_service=jwt_service,
    )

    result = await use_case.execute(
        code=request.code,
        code_verifier=request.code_verifier,
        redirect_uri=request.redirect_uri,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Invalid authorization code or code_verifier. Token exchange failed.",
            },
        )

    access_token, refresh_token, user = result

    # Commit transaction
    await session.commit()

    # Build response
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user_id=user.id,
        email=user.email,
    )

    return LoginResponse(data=token_response, error=None)


@router.post(
    "/refresh",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully refreshed tokens"},
        401: {"model": ErrorWrapper, "description": "Invalid or expired refresh token"},
    },
    summary="Refresh access token",
    description="Use refresh token to obtain new access and refresh tokens",
)
async def refresh_token(
    request: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """
    Refresh access token using refresh token.

    - Validates refresh token
    - Revokes old refresh token
    - Issues new access and refresh tokens
    """
    # Initialize dependencies
    refresh_token_repo: RefreshTokenRepository = RefreshTokenRepositoryImpl(session)
    jwt_service = JWTService()

    # Create and execute use case
    use_case = RefreshTokenUseCase(
        refresh_token_repo=refresh_token_repo, jwt_service=jwt_service
    )

    result = await use_case.execute(request.refresh_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Invalid or expired refresh token",
            },
        )

    new_access_token, new_refresh_token = result

    # Commit transaction
    await session.commit()

    # Extract user info from new access token for response
    try:
        payload = jwt_service.verify_token(new_access_token, expected_type="access")
        user_id = payload["sub"]
        email = payload.get("email", "")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to generate tokens"},
        )

    # Build response
    token_response = TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user_id,
        email=email,
    )

    return LoginResponse(data=token_response, error=None)
