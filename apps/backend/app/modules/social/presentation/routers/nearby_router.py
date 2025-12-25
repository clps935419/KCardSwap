"""
Nearby Router for Social Module
Handles nearby card search and location updates
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id
from app.modules.social.application.dtos.nearby_dtos import (
    SearchNearbyRequest as SearchRequestDTO,
)
from app.modules.social.application.use_cases.nearby import (
    RateLimitExceededException,
    SearchNearbyCardsUseCase,
    UpdateUserLocationUseCase,
)
from app.modules.social.presentation.dependencies.use_cases import (
    get_search_nearby_cards_use_case,
    get_update_user_location_use_case,
)
from app.modules.social.presentation.schemas.nearby_schemas import (
    NearbyCardResponse,
    SearchNearbyRequest,
    SearchNearbyResponse,
    UpdateLocationRequest,
)

# Create router
router = APIRouter(prefix="/nearby", tags=["Nearby Search"])


@router.post(
    "/search",
    response_model=SearchNearbyResponse,
    status_code=status.HTTP_200_OK,
    summary="Search for nearby cards",
    description="Search for cards near a specific location. Free users: 5 searches/day. Premium users: unlimited.",
    responses={
        200: {
            "description": "Search successful",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "card_id": "123e4567-e89b-12d3-a456-426614174000",
                                "owner_id": "987e6543-e21b-12d3-a456-426614174000",
                                "distance_km": 2.5,
                                "idol": "IU",
                                "idol_group": "Solo",
                                "album": "Lilac",
                                "version": "Standard",
                                "rarity": "rare",
                                "image_url": "https://storage.googleapis.com/kcardswap/cards/...",
                                "owner_nickname": "CardCollector123",
                            }
                        ],
                        "count": 1,
                    }
                }
            },
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Daily search limit exceeded: 5/5 searches used"
                    }
                }
            },
        },
    },
)
async def search_nearby_cards(
    request: SearchNearbyRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[SearchNearbyCardsUseCase, Depends(get_search_nearby_cards_use_case)],
) -> SearchNearbyResponse:
    """
    Search for cards near a specific location.
    
    Features:
    - Filters out stealth mode users
    - Sorts by distance (closest first)
    - Rate limited: 5 searches/day for free users, unlimited for premium
    - Returns card details with distance and owner information
    """
    try:
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

        return SearchNearbyResponse(results=response_results, count=len(response_results))

    except RateLimitExceededException as e:
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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update user location",
    description="Update the user's current location for nearby search visibility",
    responses={
        204: {"description": "Location updated successfully"},
        400: {"description": "Invalid coordinates"},
        404: {"description": "User profile not found"},
    },
)
async def update_user_location(
    request: UpdateLocationRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateUserLocationUseCase, Depends(get_update_user_location_use_case)],
):
    """
    Update the user's current location.
    
    This location will be used for nearby card searches.
    Users in stealth mode will not appear in search results.
    """
    try:
        # Execute update
        await use_case.execute(
            user_id=current_user_id, lat=request.lat, lng=request.lng
        )

        return None

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
