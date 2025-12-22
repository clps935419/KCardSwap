"""
Rating Router for Social Module
Handles user ratings and reviews after trades
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id
from app.modules.social.application.use_cases.ratings.rate_user_use_case import (
    RateUserUseCase,
)
from app.modules.social.infrastructure.repositories.rating_repository_impl import (
    RatingRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)
from app.modules.social.presentation.schemas.rating_schemas import (
    AverageRatingResponse,
    RatingListResponse,
    RatingRequest,
    RatingResponse,
)
from app.shared.infrastructure.database.connection import get_db_session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post(
    "",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Rating submitted successfully"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        422: {"description": "Unprocessable entity (cannot rate user)"},
        500: {"description": "Internal server error"},
    },
    summary="Submit rating",
    description="Submit a rating for another user after a trade",
)
async def submit_rating(
    request: RatingRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RatingResponse:
    """
    Submit a rating for another user.

    Business rules (FR-SOCIAL-003A):
    - Cannot rate yourself
    - Score must be between 1-5
    - Must be friends OR provide trade_id
    - Cannot rate if either party has blocked the other
    - Optional comment for detailed feedback

    Ratings help build trust in the community.
    """
    try:
        # Initialize repositories and use case
        rating_repo = RatingRepositoryImpl(session)
        friendship_repo = FriendshipRepositoryImpl(session)
        use_case = RateUserUseCase(rating_repo, friendship_repo)

        # Execute use case
        rating = await use_case.execute(
            rater_id=str(current_user_id),
            rated_user_id=str(request.rated_user_id),
            score=request.score,
            comment=request.comment,
            trade_id=str(request.trade_id) if request.trade_id else None,
        )

        return RatingResponse(
            id=UUID(rating.id),
            rater_id=UUID(rating.rater_id),
            rated_user_id=UUID(rating.rated_user_id),
            trade_id=UUID(rating.trade_id) if rating.trade_id else None,
            score=rating.score,
            comment=rating.comment,
            created_at=rating.created_at,
        )

    except ValueError as e:
        logger.warning(f"Rating validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting rating: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit rating",
        )


@router.get(
    "/user/{user_id}",
    response_model=RatingListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Ratings retrieved successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
    summary="Get user ratings",
    description="Get ratings received by a specific user",
)
async def get_user_ratings(
    user_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: int = Query(50, ge=1, le=100, description="Maximum number of ratings"),
) -> RatingListResponse:
    """
    Get ratings received by a specific user.

    Returns list of ratings with:
    - Rater information (anonymized in some cases)
    - Score and comment
    - Associated trade ID
    - Timestamp
    """
    try:
        # Initialize repository
        rating_repo = RatingRepositoryImpl(session)

        # Get ratings for user
        ratings = await rating_repo.find_by_rated_user(str(user_id), limit=limit)

        # Convert to response format
        rating_responses = [
            RatingResponse(
                id=UUID(rating.id),
                rater_id=UUID(rating.rater_id),
                rated_user_id=UUID(rating.rated_user_id),
                trade_id=UUID(rating.trade_id) if rating.trade_id else None,
                score=rating.score,
                comment=rating.comment,
                created_at=rating.created_at,
            )
            for rating in ratings
        ]

        return RatingListResponse(
            ratings=rating_responses, total=len(rating_responses)
        )

    except Exception as e:
        logger.error(f"Error getting user ratings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user ratings",
        )


@router.get(
    "/user/{user_id}/average",
    response_model=AverageRatingResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Average rating retrieved successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
    summary="Get average rating",
    description="Get average rating score for a specific user",
)
async def get_average_rating(
    user_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AverageRatingResponse:
    """
    Get average rating for a specific user.

    Returns:
    - Average score (1-5)
    - Total number of ratings received

    Useful for displaying user reputation.
    """
    try:
        # Initialize repository
        rating_repo = RatingRepositoryImpl(session)

        # Get average rating
        average_data = await rating_repo.get_average_rating(str(user_id))

        if average_data is None:
            # User has no ratings yet
            return AverageRatingResponse(
                user_id=user_id, average_score=0.0, total_ratings=0
            )

        return AverageRatingResponse(
            user_id=user_id,
            average_score=average_data["average"],
            total_ratings=average_data["count"],
        )

    except Exception as e:
        logger.error(f"Error getting average rating: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get average rating",
        )
