"""
Auth dependencies - JWT verification and user extraction
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...domain.entities.user import User
from ...domain.repositories.user_repository_interface import IUserRepository
from ...infrastructure.security.jwt_service import JWTService
from .ioc_dependencies import get_jwt_service, get_user_repository

security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> UUID:
    """
    Dependency to extract and validate current user ID from JWT token
    """
    token = credentials.credentials

    # Verify token
    payload = jwt_service.verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    try:
        return UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )


async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> User:
    """
    Dependency to get current authenticated user
    """
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def get_optional_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> Optional[UUID]:
    """
    Dependency to optionally extract user ID from JWT token
    Returns None if no token provided or invalid
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = jwt_service.verify_token(token, token_type="access")

    if not payload:
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        return UUID(user_id_str)
    except ValueError:
        return None
