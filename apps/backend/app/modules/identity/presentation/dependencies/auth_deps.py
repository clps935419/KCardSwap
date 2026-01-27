"""
Authentication Dependencies for Identity Module
Presentation layer - FastAPI dependencies for JWT authentication

NOTE:
Use shared auth dependencies to support httpOnly cookie authentication
and Bearer fallback consistently across modules.
"""

from app.shared.presentation.dependencies.auth import (  # noqa: F401
    get_current_user,
    get_current_user_id,
    get_optional_current_user_id,
)

__all__ = [
    "get_current_user",
    "get_current_user_id",
    "get_optional_current_user_id",
]
