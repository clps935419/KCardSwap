"""
Nearby Router for Social Module
Handles nearby card search and location updates
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.application.dtos.nearby_dtos import (
    SearchNearbyRequest as SearchRequestDTO,
)
from app.modules.social.application.use_cases.nearby import (
    RateLimitExceededError,
    SearchNearbyCardsUseCase,
    UpdateUserLocationUseCase,
)
from app.modules.social.domain.repositories.i_card_repository import ICardRepository
from app.modules.social.infrastructure.repositories.card_repository_impl import (
    CardRepositoryImpl,
)
from app.modules.social.infrastructure.services.search_quota_service import (
    SearchQuotaService,
)
from app.modules.social.presentation.schemas.nearby_schemas import (
    NearbyCardResponse,
    SearchNearbyRequest,
    SearchNearbyResponse,
    SearchNearbyResponseWrapper,
    UpdateLocationRequest,
    UpdateLocationResponseWrapper,
    UpdateLocationSuccess,
)
from app.shared.domain.contracts.i_profile_query_service import IProfileQueryService
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.presentation.dependencies.services import get_profile_service

# Create router
router = APIRouter(prefix="/nearby", tags=["Nearby Search"])


async def get_card_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ICardRepository:
    """Dependency: Get card repository"""
    return CardRepositoryImpl(session)


async def get_search_quota_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SearchQuotaService:
    """Dependency: Get search quota service"""
    return SearchQuotaService(session)


@router.post(
    "/search",
    response_model=SearchNearbyResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Search for nearby cards",
    description="Search for cards near a specific location. Free users: 5 searches/day. Premium users: unlimited.",
    responses={
        200: {"description": "Search successful"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def search_nearby_cards(
    request: SearchNearbyRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    card_repository: Annotated[ICardRepository, Depends(get_card_repository)],
    quota_service: Annotated[SearchQuotaService, Depends(get_search_quota_service)],
) -> SearchNearbyResponseWrapper:
    """
    Search for cards near a specific location.

    Features:
    - Filters out stealth mode users
    - Sorts by distance (closest first)
    - Rate limited: 5 searches/day for free users, unlimited for premium
    - Returns card details with distance and owner information
    """
    try:
        # Create use case
        use_case = SearchNearbyCardsUseCase(
            card_repository=card_repository,
            quota_service=quota_service,
        )

        # Execute search
        # TODO(Phase 8): Check if user is premium from subscription status
        # For now, assume all users are free (will be implemented in Phase 8: US6)
        is_premium = False

        dto_request = SearchRequestDTO(
            user_id=current_user_id,
            lat=request.lat,
            lng=request.lng,
            radius_km=request.radius_km,
        )

        results = await use_case.execute(dto_request, is_premium=is_premium)

        # Convert to response
        response_results = [
            NearbyCardResponse(
                card_id=r.card_id,
                owner_id=r.owner_id,
                distance_km=r.distance_km,
                idol=r.idol,
                idol_group=r.idol_group,
                album=r.album,
                version=r.version,
                rarity=r.rarity,
                image_url=r.image_url,
                owner_nickname=r.owner_nickname,
            )
            for r in results
        ]

        data = SearchNearbyResponse(
            results=response_results, count=len(response_results)
        )
        return SearchNearbyResponseWrapper(data=data, meta=None, error=None)

    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search nearby cards: {str(e)}",
        )


@router.put(
    "/location",
    response_model=UpdateLocationResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Update user location",
    description="Update the user's current location for nearby search visibility",
    responses={
        200: {"description": "Location updated successfully"},
        400: {"description": "Invalid coordinates"},
        404: {"description": "User profile not found"},
    },
)
async def update_user_location(
    request: UpdateLocationRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    profile_service: Annotated[IProfileQueryService, Depends(get_profile_service)],
) -> UpdateLocationResponseWrapper:
    """
    Update the user's current location.

    This location will be used for nearby card searches.
    Users in stealth mode will not appear in search results.
    """
    try:
        # Create use case
        use_case = UpdateUserLocationUseCase(profile_service=profile_service)

        # Execute update
        await use_case.execute(
            user_id=current_user_id, lat=request.lat, lng=request.lng
        )

        data = UpdateLocationSuccess(success=True, message="Location updated successfully")
        return UpdateLocationResponseWrapper(data=data, meta=None, error=None)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update location: {str(e)}",
        )
