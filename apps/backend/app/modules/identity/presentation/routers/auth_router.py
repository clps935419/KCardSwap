"""
Authentication Router for Identity Module
Handles Google login, token refresh, and logout
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

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
from app.modules.identity.application.use_cases.auth.logout import LogoutUseCase
from app.modules.identity.application.use_cases.auth.refresh_token import (
    RefreshTokenUseCase,
)
from app.modules.identity.presentation.dependencies.auth_deps import (
    get_current_user_id,
)
from app.modules.identity.presentation.dependencies.use_cases import (
    get_admin_login_use_case,
    get_google_callback_use_case,
    get_google_login_use_case,
    get_logout_use_case,
    get_refresh_token_use_case,
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
    use_case: Annotated[AdminLoginUseCase, Depends(get_admin_login_use_case)],
) -> LoginResponse:
    """
    Admin login with email/password.

    - Verifies email and password
    - Checks if user has admin role (admin or super_admin)
    - Returns JWT access and refresh tokens

    This endpoint is only for admin users with password-based authentication.
    Regular users should use Google OAuth login.
    """
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
    use_case: Annotated[GoogleCallbackUseCase, Depends(get_google_callback_use_case)],
) -> LoginResponse:
    """
    Login with Google OAuth.

    - Verifies Google ID token
    - Creates user and profile if new user
    - Returns JWT access and refresh tokens
    """
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
    use_case: Annotated[RefreshTokenUseCase, Depends(get_refresh_token_use_case)],
) -> LoginResponse:
    """
    Refresh access token using refresh token.

    - Validates refresh token
    - Revokes old refresh token
    - Issues new access and refresh tokens
    """
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

    # Extract user info from new access token for response
    from app.shared.infrastructure.security.jwt_service import JWTService
    jwt_service = JWTService()
    
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
