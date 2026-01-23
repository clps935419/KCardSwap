"""Shared Dependency: Require User (Enforces Authentication).

This dependency ensures that all endpoints requiring authentication
have a consistent way to verify user login status.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.shared.presentation.dependencies.auth import get_current_user_id


async def require_user(
    current_user_id: UUID = Depends(get_current_user_id),
) -> UUID:
    """Dependency that enforces user authentication.

    This is a wrapper around get_current_user_id that provides
    a clear semantic meaning: "this endpoint requires login".

    Args:
        current_user_id: User ID from JWT token (auto-injected)

    Returns:
        User ID (UUID)

    Raises:
        HTTPException: 401 if not authenticated

    Usage:
        @router.get("/posts")
        async def list_posts(user_id: UUID = Depends(require_user)):
            # user_id is guaranteed to be valid here
            ...
    """
    if current_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "401_UNAUTHORIZED",
                "message": "Authentication required to access this resource",
            },
        )
    return current_user_id
