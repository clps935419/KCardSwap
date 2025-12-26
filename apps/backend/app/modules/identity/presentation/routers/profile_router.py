"""
Profile Router for Identity Module
Handles user profile retrieval and updates
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.application.use_cases.profile.get_profile import (
    GetProfileUseCase,
)
from app.modules.identity.application.use_cases.profile.update_profile import (
    UpdateProfileUseCase,
)
from app.modules.identity.presentation.dependencies.auth_deps import get_current_user
from app.modules.identity.presentation.dependencies.use_case_deps import (
    get_get_profile_use_case,
    get_update_profile_use_case,
)
from app.modules.identity.presentation.schemas.profile_schemas import (
    ProfileErrorWrapper,
    ProfileResponse,
    ProfileResponseWrapper,
    UpdateProfileRequest,
)
from app.shared.infrastructure.database.connection import get_db_session

# Create router
router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get(
    "/me",
    response_model=ProfileResponseWrapper,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully retrieved profile"},
        401: {"model": ProfileErrorWrapper, "description": "Unauthorized"},
        404: {"model": ProfileErrorWrapper, "description": "Profile not found"},
    },
    summary="Get my profile",
    description="Retrieve the authenticated user's profile information",
)
async def get_my_profile(
    current_user_id: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[GetProfileUseCase, Depends(get_get_profile_use_case)],
) -> ProfileResponseWrapper:
    """
    Get current user's profile.

    Requires authentication (Bearer token).
    """
    # Execute use case
    profile = await use_case.execute(current_user_id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Profile not found"},
        )

    # Build response
    profile_response = ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        nickname=profile.nickname,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        region=profile.region,
        preferences=profile.preferences or {},
        privacy_flags=profile.privacy_flags
        or {"nearby_visible": True, "show_online": True, "allow_stranger_chat": True},
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )

    return ProfileResponseWrapper(data=profile_response, error=None)


@router.put(
    "/me",
    response_model=ProfileResponseWrapper,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully updated profile"},
        400: {"model": ProfileErrorWrapper, "description": "Validation error"},
        401: {"model": ProfileErrorWrapper, "description": "Unauthorized"},
    },
    summary="Update my profile",
    description="Update the authenticated user's profile information",
)
async def update_my_profile(
    request: UpdateProfileRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[UpdateProfileUseCase, Depends(get_update_profile_use_case)],
) -> ProfileResponseWrapper:
    """
    Update current user's profile.

    Requires authentication (Bearer token).
    Can update any combination of profile fields.
    """
    # Execute use case
    profile = await use_case.execute(
        user_id=current_user_id,
        nickname=request.nickname,
        avatar_url=request.avatar_url,
        bio=request.bio,
        region=request.region,
        preferences=request.preferences,
        privacy_flags=request.privacy_flags,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to update profile"},
        )

    # Commit transaction
    await session.commit()

    # Build response
    profile_response = ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        nickname=profile.nickname,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        region=profile.region,
        preferences=profile.preferences or {},
        privacy_flags=profile.privacy_flags
        or {"nearby_visible": True, "show_online": True, "allow_stranger_chat": True},
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )

    return ProfileResponseWrapper(data=profile_response, error=None)
