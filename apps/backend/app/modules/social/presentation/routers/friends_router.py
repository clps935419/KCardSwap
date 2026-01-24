"""
Friends Router for Social Module - POC Version
Only includes blocking functionality as per FR-025
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.application.use_cases.friends.block_user_use_case import (
    BlockUserUseCase,
)
from app.modules.social.application.use_cases.friends.unblock_user_use_case import (
    UnblockUserUseCase,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)
from app.modules.social.presentation.schemas.friends_schemas import (
    BlockUserRequest,
    UnblockUserRequest,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/friends", tags=["Friends"])


@router.post(
    "/block",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
    summary="Block a user",
    description="Block a user to prevent interaction. Required for FR-025 (blocking support).",
)
async def block_user(
    request: BlockUserRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Block a user.

    Prevents:
    - Private messaging
    - Friend requests
    - Viewing posts (optional)
    """
    try:
        friendship_repo = FriendshipRepositoryImpl(session)
        use_case = BlockUserUseCase(friendship_repository=friendship_repo)

        await use_case.execute(
            blocker_id=str(current_user_id), blocked_id=str(request.user_id)
        )

        return {"message": "User blocked successfully", "error": None}
    except ValueError as e:
        logger.warning(f"Block user validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error blocking user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to block user",
        )


@router.post(
    "/unblock",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
    summary="Unblock a user",
    description="Unblock a previously blocked user. Required for FR-025.",
)
async def unblock_user(
    request: UnblockUserRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Unblock a user.

    Restores normal interaction capabilities.
    """
    try:
        friendship_repo = FriendshipRepositoryImpl(session)
        use_case = UnblockUserUseCase(friendship_repository=friendship_repo)

        await use_case.execute(
            blocker_id=str(current_user_id), blocked_id=str(request.user_id)
        )

        return {"message": "User unblocked successfully", "error": None}
    except ValueError as e:
        logger.warning(f"Unblock user validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error unblocking user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unblock user",
        )
