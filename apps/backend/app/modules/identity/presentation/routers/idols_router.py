"""Idols router for idol group endpoints."""

from fastapi import APIRouter

from app.modules.identity.infrastructure.data.idol_groups import get_all_idol_groups
from app.modules.identity.presentation.schemas.idol_schemas import (
    IdolGroupListResponse,
    IdolGroupListResponseWrapper,
    IdolGroupResponse,
)

router = APIRouter(prefix="/idols", tags=["idols"])


@router.get(
    "/groups",
    response_model=IdolGroupListResponseWrapper,
    summary="Get all idol groups",
    description="""
    Get a list of all available K-pop idol groups for onboarding.

    This endpoint provides the complete list of idol groups that users can select
    during the onboarding process to indicate their preferences.

    Each idol group includes:
    - `id`: Unique identifier (e.g., newjeans, ive, aespa)
    - `name`: Display name (e.g., NewJeans, IVE, aespa)
    - `emoji`: Emoji representing the group (e.g., 👖, 🦢, 🦋)

    This is a **public endpoint** that **does not require authentication**.
    Frontend applications should use this to dynamically populate idol group selection.
    """,
    responses={
        200: {
            "description": "List of all idol groups retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "groups": [
                                {"id": "newjeans", "name": "NewJeans", "emoji": "👖"},
                                {"id": "ive", "name": "IVE", "emoji": "🦢"},
                                {"id": "aespa", "name": "aespa", "emoji": "🦋"},
                            ]
                        },
                        "meta": None,
                        "error": None,
                    }
                }
            },
        }
    },
)
async def get_idol_groups() -> IdolGroupListResponseWrapper:
    """Get all available idol groups.

    Returns:
        List of all idol groups with id, name, and emoji
    """
    idol_groups = get_all_idol_groups()

    group_responses = [
        IdolGroupResponse(id=group.id, name=group.name, emoji=group.emoji)
        for group in idol_groups
    ]

    data = IdolGroupListResponse(groups=group_responses)
    return IdolGroupListResponseWrapper(data=data, meta=None, error=None)
