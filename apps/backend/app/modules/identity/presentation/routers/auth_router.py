"""
Authentication Router for Identity Module
Handles Google login, token refresh, and logout
"""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

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
from app.modules.identity.presentation.dependencies.use_case_deps import (
    get_admin_login_use_case,
    get_google_callback_use_case,
    get_google_login_use_case,
    get_refresh_token_use_case,
)
from app.modules.identity.presentation.schemas.auth_schemas import (
    AdminLoginRequest,
    GoogleCallbackRequest,
    GoogleLoginRequest,
    LoginResponse,
    RefreshSuccessResponse,
    RefreshTokenRequest,
    TokenResponse,
)
from app.shared.infrastructure.security.jwt_service import JWTService

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/admin-login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully authenticated as admin"},
        400: {"description": "Validation error"},
        401: {"description": "Invalid credentials or not an admin"},
    },
    summary="Admin login with email/password",
    description="Authenticate admin user with email and password and receive JWT tokens",
)
async def admin_login(
    request: AdminLoginRequest,
    use_case: Annotated[AdminLoginUseCase, Depends(get_admin_login_use_case)],
) -> LoginResponse:
    """
    Admin login with email/password.

    - Verifies email and password
    - Checks if user has admin role
    - Returns JWT access and refresh tokens
    """
    # Execute use case
    result = await use_case.execute(request.email, request.password)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Invalid credentials or not an admin",
            },
        )

    access_token, refresh_token, user = result

    # Build response
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert minutes to seconds for expires_in field
        user_id=user.id,
        email=user.email,
        role=user.role,  # Include user role in response
    )

    return LoginResponse(data=token_response, meta=None, error=None)


@router.post(
    "/google-login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully authenticated"},
        400: {"description": "Validation error"},
        401: {"description": "Invalid Google token"},
    },
    summary="Login with Google",
    description="Authenticate user with Google OAuth token and receive JWT tokens",
)
async def google_login(
    request: GoogleLoginRequest,
    use_case: Annotated[GoogleLoginUseCase, Depends(get_google_login_use_case)],
) -> LoginResponse:
    """
    Login with Google OAuth.

    - Verifies Google ID token
    - Creates user and profile if new user
    - Returns JWT access and refresh tokens
    """
    # Execute use case
    result = await use_case.execute(request.google_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid Google token"},
        )

    access_token, refresh_token, user = result

    # Build response
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user_id=user.id,
        email=user.email,
    )

    return LoginResponse(data=token_response, meta=None, error=None)


@router.post(
    "/google-callback",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully authenticated"},
        400: {"description": "Validation error"},
        401: {"description": "Invalid authorization code or code_verifier"},
        422: {"description": "Token exchange failed"},
    },
    summary="Google OAuth Callback with PKCE",
    description="Authenticate user with Google OAuth authorization code and PKCE code_verifier (Expo AuthSession)",
)
async def google_callback(
    request: GoogleCallbackRequest,
    use_case: Annotated[GoogleCallbackUseCase, Depends(get_google_callback_use_case)],
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
    # Execute use case
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

    # Build response
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user_id=user.id,
        email=user.email,
    )

    return LoginResponse(data=token_response, meta=None, error=None)


@router.post(
    "/refresh",
    response_model=RefreshSuccessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully refreshed tokens"},
        401: {"description": "Invalid or expired refresh token"},
    },
    summary="Refresh access token (cookie-based)",
    description="Use refresh token from httpOnly cookie to obtain new access and refresh tokens",
)
async def refresh_token(
    response: Response,
    use_case: Annotated[RefreshTokenUseCase, Depends(get_refresh_token_use_case)],
    jwt_service: JWTService = Depends(lambda: JWTService()),
    refresh_token_cookie: str | None = Cookie(None, alias=settings.REFRESH_COOKIE_NAME),
) -> RefreshSuccessResponse:
    """
    Refresh access token using refresh token from httpOnly cookie.

    - Reads refresh_token from httpOnly cookie
    - Validates refresh token
    - Revokes old refresh token
    - Issues new access and refresh tokens
    - Sets new tokens as httpOnly cookies
    """
    # Check if refresh token exists in cookie
    if not refresh_token_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Refresh token not found in cookie",
            },
        )

    # Execute use case
    result = await use_case.execute(refresh_token_cookie)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Invalid or expired refresh token",
            },
        )

    new_access_token, new_refresh_token = result

    # Set new tokens as httpOnly cookies
    # Access token cookie
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=new_access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=settings.COOKIE_HTTPONLY,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
        domain=settings.COOKIE_DOMAIN,
        path=settings.COOKIE_PATH,
    )

    # Refresh token cookie
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=new_refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=settings.COOKIE_HTTPONLY,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
        domain=settings.COOKIE_DOMAIN,
        path=settings.COOKIE_PATH,
    )

    return RefreshSuccessResponse(
        success=True,
        message="Tokens refreshed successfully",
    )
