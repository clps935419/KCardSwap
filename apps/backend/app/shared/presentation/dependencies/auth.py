"""
Shared Authentication Dependencies

FastAPI dependencies for JWT authentication that can be used across all modules.
Moved from Identity module to shared layer for proper separation of concerns.
"""

from typing import Optional
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.config import settings
from app.shared.infrastructure.security.jwt_service import JWTService

# HTTP Bearer security scheme (optional for backward compatibility)
# auto_error=False allows checking cookie first, then falling back to Bearer token
security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token_cookie: Optional[str] = Cookie(None, alias=settings.ACCESS_COOKIE_NAME),
    jwt_service: JWTService = Depends(lambda: JWTService()),
) -> UUID:
    """
    Dependency to get current authenticated user ID from JWT token.

    Priority:
    1. First checks httpOnly cookie for access_token (recommended)
    2. Falls back to Bearer token in Authorization header (for backward compatibility)

    Args:
        credentials: Optional HTTP Bearer credentials (JWT token)
        access_token_cookie: Optional access token from httpOnly cookie
        jwt_service: JWT service instance

    Returns:
        User ID (UUID)

    Raises:
        HTTPException: 401 if token is invalid or missing
    """
    # Priority 1: Check httpOnly cookie first (most secure)
    token = access_token_cookie

    # Priority 2: Fallback to Bearer token (backward compatibility)
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing authentication token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verify token and extract payload
        payload = jwt_service.verify_token(token, expected_type="access")
        user_id_str: Optional[str] = payload.get("sub")

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "Invalid token: missing subject",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert to UUID
        user_id = UUID(user_id_str)
        return user_id

    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": f"Invalid or expired token: {str(e)}",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(user_id: UUID = Depends(get_current_user_id)) -> UUID:
    """
    Dependency to get current authenticated user.
    Alias for get_current_user_id for backward compatibility.

    Args:
        user_id: User ID from JWT token

    Returns:
        User ID (UUID)
    """
    return user_id


async def get_optional_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token_cookie: Optional[str] = Cookie(None, alias=settings.ACCESS_COOKIE_NAME),
    jwt_service: JWTService = Depends(lambda: JWTService()),
) -> Optional[UUID]:
    """
    Dependency to optionally get current user ID from JWT token.
    Returns None if no token is provided or token is invalid.
    Useful for endpoints that work both with and without authentication.

    Priority:
    1. First checks httpOnly cookie for access_token
    2. Falls back to Bearer token in Authorization header

    Args:
        credentials: Optional HTTP Bearer credentials
        access_token_cookie: Optional access token from httpOnly cookie
        jwt_service: JWT service instance

    Returns:
        User ID (UUID) or None
    """
    # Priority 1: Check httpOnly cookie first
    token = access_token_cookie

    # Priority 2: Fallback to Bearer token
    if not token and credentials:
        token = credentials.credentials

    if not token:
        return None

    try:
        payload = jwt_service.verify_token(token, expected_type="access")
        user_id_str = payload.get("sub")

        if user_id_str is None:
            return None

        return UUID(user_id_str)
    except (JWTError, ValueError):
        return None
