"""
Shared Presentation Dependencies

Common FastAPI dependencies that can be used across all modules.
"""

from app.shared.presentation.dependencies.auth import (
    get_current_user,
    get_current_user_id,
    get_optional_current_user_id,
)
from app.shared.presentation.dependencies.services import (
    get_profile_service,
    get_subscription_service,
)

__all__ = [
    "get_current_user_id",
    "get_current_user",
    "get_optional_current_user_id",
    "get_profile_service",
    "get_subscription_service",
]
