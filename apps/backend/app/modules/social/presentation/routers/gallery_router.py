"""
Gallery Cards Router for Social Module.
Handles personal gallery card management (User Story 2).
"""
import logging
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.application.use_cases.reorder_gallery_cards import (
    ReorderGalleryCardsUseCase,
)
from app.modules.social.domain.entities.gallery_card import GalleryCard
from app.modules.social.domain.repositories.i_gallery_card_repository import (
    IGalleryCardRepository,
)
from app.modules.social.infrastructure.repositories.gallery_card_repository import (
    GalleryCardRepository,
)
from app.modules.social.presentation.schemas.gallery_schemas import (
    CreateGalleryCardRequest,
    GalleryCardListResponse,
    GalleryCardListResponseWrapper,
    GalleryCardResponse,
    GalleryCardResponseWrapper,
    ReorderGalleryCardsRequest,
    ReorderGalleryCardsResponse,
    ReorderGalleryCardsResponseWrapper,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import require_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["Gallery"])


def get_gallery_card_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> IGalleryCardRepository:
    """Dependency to get gallery card repository."""
    return GalleryCardRepository(session)


@router.get(
    "/users/{user_id}/gallery/cards",
    response_model=GalleryCardListResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get user's gallery cards",
    description="View another user's public gallery cards (requires authentication).",
)
async def get_user_gallery_cards(
    user_id: UUID,
    current_user_id: Annotated[UUID, Depends(require_user)],
    repository: Annotated[IGalleryCardRepository, Depends(get_gallery_card_repository)],
):
    """Get a user's gallery cards."""
    try:
        cards = await repository.find_by_user_id(user_id)
        total = await repository.count_by_user_id(user_id)

        return {
            "data": GalleryCardListResponse(
                items=[
                    GalleryCardResponse(
                        id=card.id,
                        user_id=card.user_id,
                        title=card.title,
                        idol_name=card.idol_name,
                        era=card.era,
                        description=card.description,
                        media_asset_id=card.media_asset_id,
                        display_order=card.display_order,
                        created_at=card.created_at,
                        updated_at=card.updated_at,
                    )
                    for card in cards
                ],
                total=total,
            ),
            "meta": None,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Error getting user gallery cards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gallery cards",
        )


@router.get(
    "/gallery/cards/me",
    response_model=GalleryCardListResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get my gallery cards",
    description="Get the authenticated user's own gallery cards.",
)
async def get_my_gallery_cards(
    current_user_id: Annotated[UUID, Depends(require_user)],
    repository: Annotated[IGalleryCardRepository, Depends(get_gallery_card_repository)],
):
    """Get the current user's gallery cards."""
    user_id = current_user_id

    try:
        cards = await repository.find_by_user_id(user_id)
        total = await repository.count_by_user_id(user_id)

        return {
            "data": GalleryCardListResponse(
                items=[
                    GalleryCardResponse(
                        id=card.id,
                        user_id=card.user_id,
                        title=card.title,
                        idol_name=card.idol_name,
                        era=card.era,
                        description=card.description,
                        media_asset_id=card.media_asset_id,
                        display_order=card.display_order,
                        created_at=card.created_at,
                        updated_at=card.updated_at,
                    )
                    for card in cards
                ],
                total=total,
            ),
            "meta": None,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Error getting my gallery cards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gallery cards",
        )


@router.post(
    "/gallery/cards",
    response_model=GalleryCardResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Create gallery card",
    description="Create a new gallery card in the user's personal album.",
)
async def create_gallery_card(
    request: CreateGalleryCardRequest,
    current_user_id: Annotated[UUID, Depends(require_user)],
    repository: Annotated[IGalleryCardRepository, Depends(get_gallery_card_repository)],
):
    """Create a new gallery card."""
    user_id = current_user_id

    try:
        # Get current max display_order for this user
        existing_cards = await repository.find_by_user_id(user_id)
        next_order = len(existing_cards)

        # Create new card
        new_card = GalleryCard(
            id=uuid4(),
            user_id=user_id,
            title=request.title,
            idol_name=request.idol_name,
            era=request.era,
            description=request.description,
            display_order=next_order,
        )

        created_card = await repository.create(new_card)

        return {
            "data": GalleryCardResponse(
                id=created_card.id,
                user_id=created_card.user_id,
                title=created_card.title,
                idol_name=created_card.idol_name,
                era=created_card.era,
                description=created_card.description,
                media_asset_id=created_card.media_asset_id,
                display_order=created_card.display_order,
                created_at=created_card.created_at,
                updated_at=created_card.updated_at,
            ),
            "meta": None,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Error creating gallery card: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create gallery card",
        )


@router.delete(
    "/gallery/cards/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete gallery card",
    description="Delete a gallery card (only owner can delete).",
)
async def delete_gallery_card(
    card_id: UUID,
    current_user_id: Annotated[UUID, Depends(require_user)],
    repository: Annotated[IGalleryCardRepository, Depends(get_gallery_card_repository)],
):
    """Delete a gallery card."""
    user_id = current_user_id

    try:
        # Check if card exists and belongs to user
        card = await repository.find_by_id(card_id)

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallery card not found",
            )

        if card.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own gallery cards",
            )

        # Delete the card
        deleted = await repository.delete(card_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallery card not found",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting gallery card: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete gallery card",
        )


@router.put(
    "/gallery/cards/reorder",
    response_model=ReorderGalleryCardsResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Reorder gallery cards",
    description="Update the display order of gallery cards.",
)
async def reorder_gallery_cards(
    request: ReorderGalleryCardsRequest,
    current_user_id: Annotated[UUID, Depends(require_user)],
    repository: Annotated[IGalleryCardRepository, Depends(get_gallery_card_repository)],
):
    """Reorder gallery cards."""
    user_id = current_user_id

    try:
        use_case = ReorderGalleryCardsUseCase(repository)
        updated_cards = await use_case.execute(user_id, request.card_ids)

        return {
            "data": ReorderGalleryCardsResponse(
                message="Gallery cards reordered successfully",
                updated_count=len(updated_cards),
            ),
            "meta": None,
            "error": None,
        }
    except ValueError as e:
        logger.warning(f"Invalid reorder request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error reordering gallery cards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder gallery cards",
        )
