"""
Profile Router - Profile management endpoints
GET /api/v1/profile/me - Get own profile
PATCH /api/v1/profile/me - Update own profile
"""
from uuid import UUID

from fastapi import APIRouter, Depends

from ...application.use_cases.profile import GetProfileUseCase, UpdateProfileUseCase
from ...domain.repositories.profile_repository_interface import IProfileRepository
from ..dependencies import get_current_user_id
from ..dependencies.ioc_dependencies import get_profile_repository
from ..schemas import APIResponse, ErrorDetail, ProfileResponse, UpdateProfileRequest

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.get("/me", response_model=APIResponse)
async def get_my_profile(
    user_id: UUID = Depends(get_current_user_id),
    profile_repo: IProfileRepository = Depends(get_profile_repository)
):
    """
    Get current user's profile

    Requires authentication.
    """
    use_case = GetProfileUseCase(profile_repo=profile_repo)

    profile = await use_case.execute(user_id)

    if not profile:
        return APIResponse(
            data=None,
            error=ErrorDetail(
                code="NOT_FOUND",
                message="Profile not found"
            ).dict()
        )

    return APIResponse(
        data=ProfileResponse(
            user_id=profile.user_id,
            nickname=profile.nickname,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            region=profile.region,
            preferences=profile.preferences,
            privacy_flags=profile.privacy_flags
        ).dict(),
        error=None
    )


@router.patch("/me", response_model=APIResponse)
async def update_my_profile(
    request: UpdateProfileRequest,
    user_id: UUID = Depends(get_current_user_id),
    profile_repo: IProfileRepository = Depends(get_profile_repository)
):
    """
    Update current user's profile

    Requires authentication.
    Can update nickname, avatar, bio, region, preferences, and privacy settings.
    """
    use_case = UpdateProfileUseCase(profile_repo=profile_repo)

    profile = await use_case.execute(
        user_id=user_id,
        nickname=request.nickname,
        avatar_url=request.avatar_url,
        bio=request.bio,
        region=request.region,
        preferences=request.preferences,
        privacy_flags=request.privacy_flags
    )

    if not profile:
        return APIResponse(
            data=None,
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="Failed to update profile"
            ).dict()
        )

    return APIResponse(
        data=ProfileResponse(
            user_id=profile.user_id,
            nickname=profile.nickname,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            region=profile.region,
            preferences=profile.preferences,
            privacy_flags=profile.privacy_flags
        ).dict(),
        error=None
    )
