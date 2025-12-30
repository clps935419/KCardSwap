"""
Friends Router for Social Module
Handles friend requests, acceptance, blocking, and friend list
"""

import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id
from app.modules.social.application.use_cases.friends.accept_friend_request_use_case import (
    AcceptFriendRequestUseCase,
)
from app.modules.social.application.use_cases.friends.block_user_use_case import (
    BlockUserUseCase,
)
from app.modules.social.application.use_cases.friends.send_friend_request_use_case import (
    SendFriendRequestUseCase,
)
from app.modules.social.application.use_cases.friends.unblock_user_use_case import (
    UnblockUserUseCase,
)
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)
from app.modules.social.presentation.schemas.friends_schemas import (
    BlockUserRequest,
    FriendListResponse,
    FriendshipResponse,
    SendFriendRequestRequest,
    UnblockUserRequest,
)
from app.shared.infrastructure.database.connection import get_db_session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/friends", tags=["Friends"])


@router.post(
    "/request",
    response_model=FriendshipResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Friend request sent successfully"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        422: {
            "description": "Unprocessable entity (cannot send request - already friends, pending, or blocked)"
        },
        500: {"description": "Internal server error"},
    },
    summary="Send friend request",
    description="Send a friend request to another user",
)
async def send_friend_request(
    request: SendFriendRequestRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FriendshipResponse:
    """
    Send a friend request to another user.

    Business rules:
    - Cannot send request to yourself
    - Cannot send request if already friends
    - Cannot send request if pending request exists
    - Cannot send request if user is blocked
    """
    try:
        # Initialize repository and use case
        friendship_repo = FriendshipRepositoryImpl(session)
        use_case = SendFriendRequestUseCase(friendship_repo)

        # Execute use case
        friendship = await use_case.execute(
            user_id=str(current_user_id), friend_id=str(request.friend_id)
        )

        return FriendshipResponse(
            id=UUID(friendship.id),
            user_id=UUID(friendship.user_id),
            friend_id=UUID(friendship.friend_id),
            status=friendship.status.value,
            created_at=friendship.created_at,
        )

    except ValueError as e:
        logger.warning(f"Friend request validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending friend request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send friend request",
        )


@router.post(
    "/{friendship_id}/accept",
    response_model=FriendshipResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Friend request accepted successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        403: {"description": "Forbidden (not authorized to accept this request)"},
        404: {"description": "Friend request not found"},
        422: {"description": "Unprocessable entity (request cannot be accepted)"},
        500: {"description": "Internal server error"},
    },
    summary="Accept friend request",
    description="Accept a pending friend request",
)
async def accept_friend_request(
    friendship_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FriendshipResponse:
    """
    Accept a pending friend request.

    Business rules:
    - Only the recipient can accept the request
    - Request must be in pending status
    """
    try:
        # Initialize repositories and use case
        friendship_repo = FriendshipRepositoryImpl(session)
        chat_room_repo = ChatRoomRepositoryImpl(session)
        use_case = AcceptFriendRequestUseCase(friendship_repo, chat_room_repo)

        # Execute use case
        friendship, chat_room = await use_case.execute(
            friendship_id=str(friendship_id), accepting_user_id=str(current_user_id)
        )

        return FriendshipResponse(
            id=UUID(friendship.id),
            user_id=UUID(friendship.user_id),
            friend_id=UUID(friendship.friend_id),
            status=friendship.status.value,
            created_at=friendship.created_at,
        )

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "not authorized" in error_msg or "only" in error_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
    except Exception as e:
        logger.error(f"Error accepting friend request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept friend request",
        )


@router.post(
    "/block",
    response_model=FriendshipResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User blocked successfully"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        422: {"description": "Unprocessable entity (cannot block user)"},
        500: {"description": "Internal server error"},
    },
    summary="Block user",
    description="Block another user (prevents all interactions)",
)
async def block_user(
    request: BlockUserRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FriendshipResponse:
    """
    Block another user.

    Business rules:
    - Cannot block yourself
    - Blocking removes any existing friendship
    - Blocked users cannot send messages or interact
    """
    try:
        # Initialize repository and use case
        friendship_repo = FriendshipRepositoryImpl(session)
        use_case = BlockUserUseCase(friendship_repo)

        # Execute use case
        friendship = await use_case.execute(
            blocker_id=str(current_user_id), blocked_id=str(request.user_id)
        )

        return FriendshipResponse(
            id=UUID(friendship.id),
            user_id=UUID(friendship.user_id),
            friend_id=UUID(friendship.friend_id),
            status=friendship.status.value,
            created_at=friendship.created_at,
        )

    except ValueError as e:
        logger.warning(f"Block user validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error blocking user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to block user",
        )


@router.post(
    "/unblock",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "User unblocked successfully (no content)"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        404: {"description": "No blocked relationship found"},
        422: {"description": "Unprocessable entity (cannot unblock user)"},
        500: {"description": "Internal server error"},
    },
    summary="Unblock user",
    description="Unblock a previously blocked user (allows future interactions)",
)
async def unblock_user(
    request: UnblockUserRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """
    Unblock a previously blocked user.

    Business rules:
    - Can only unblock if you were the one who blocked them
    - Unblocking removes the blocked relationship entirely
    - After unblocking, users can interact again (send friend requests, chat)
    - Does not automatically make them friends
    - Cannot unblock yourself
    """
    try:
        # Initialize repository and use case
        friendship_repo = FriendshipRepositoryImpl(session)
        use_case = UnblockUserUseCase(friendship_repo)

        # Execute use case
        await use_case.execute(
            unblocker_user_id=str(current_user_id), unblocked_user_id=str(request.user_id)
        )

        # Return 204 No Content (no response body for successful deletion)
        return None

    except ValueError as e:
        error_msg = str(e).lower()
        if "no relationship exists" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )
        else:
            logger.warning(f"Unblock user validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
    except Exception as e:
        logger.error(f"Error unblocking user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unblock user",
        )


@router.get(
    "",
    response_model=FriendListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Friend list retrieved successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        500: {"description": "Internal server error"},
    },
    summary="Get friend list",
    description="Get list of friends (optionally filtered by status)",
)
async def get_friends(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by friendship status (accepted, pending, blocked). If not provided, returns all friendships.",
    ),
) -> FriendListResponse:
    """
    Get list of friends for the current user.

    Can be filtered by status:
    - accepted: Only accepted friendships
    - pending: Only pending friend requests
    - blocked: Only blocked users
    """
    try:
        # Initialize repository
        friendship_repo = FriendshipRepositoryImpl(session)

        # Get friendships by status
        friendships = await friendship_repo.find_by_user_and_status(
            str(current_user_id), status_filter
        )

        # Convert to response format
        # Note: In a real implementation, we would fetch user profiles
        # For now, return basic friendship data
        from app.modules.social.presentation.schemas.friends_schemas import (
            FriendListItemResponse,
        )

        friends = [
            FriendListItemResponse(
                id=UUID(f.id),
                user_id=UUID(
                    f.friend_id if f.user_id == str(current_user_id) else f.user_id
                ),
                nickname=None,  # TODO: Fetch from profile
                avatar_url=None,  # TODO: Fetch from profile
                status=f.status.value,
                created_at=f.created_at,
            )
            for f in friendships
        ]

        return FriendListResponse(friends=friends, total=len(friends))

    except Exception as e:
        logger.error(f"Error getting friend list: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get friend list",
        )
