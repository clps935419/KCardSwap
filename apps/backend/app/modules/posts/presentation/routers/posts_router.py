"""
Posts Router for Posts Module
Handles city board posts and interest management
"""

import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id
from app.modules.posts.application.use_cases.create_post_use_case import CreatePostUseCase
from app.modules.posts.application.use_cases.list_board_posts_use_case import ListBoardPostsUseCase
from app.modules.posts.application.use_cases.express_interest_use_case import ExpressInterestUseCase
from app.modules.posts.application.use_cases.accept_interest_use_case import AcceptInterestUseCase
from app.modules.posts.application.use_cases.reject_interest_use_case import RejectInterestUseCase
from app.modules.posts.application.use_cases.close_post_use_case import ClosePostUseCase
from app.modules.posts.infrastructure.repositories.post_repository_impl import PostRepositoryImpl
from app.modules.posts.infrastructure.repositories.post_interest_repository_impl import PostInterestRepositoryImpl
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
from app.modules.social.infrastructure.repositories.friendship_repository_impl import FriendshipRepositoryImpl
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import ChatRoomRepositoryImpl
from app.modules.posts.presentation.schemas.post_schemas import (
    CreatePostRequest,
    PostResponse,
    PostListResponse,
    PostInterestResponse,
    AcceptInterestResponse,
)
from app.shared.infrastructure.database.connection import get_db_session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Post created successfully"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        422: {"description": "Unprocessable entity (daily limit exceeded or validation failed)"},
        500: {"description": "Internal server error"},
    },
    summary="Create a new city board post",
    description="Create a new post on a city board. Free users limited to 2 posts per day.",
)
async def create_post(
    request: CreatePostRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostResponse:
    """
    Create a new city board post.

    Business rules:
    - Free users: 2 posts per day
    - Premium users: unlimited posts
    - Posts expire after 14 days by default
    """
    try:
        # Initialize repositories and use case
        post_repo = PostRepositoryImpl(session)
        subscription_repo = SubscriptionRepositoryImpl(session)
        use_case = CreatePostUseCase(post_repo, subscription_repo)

        # Execute use case
        post = await use_case.execute(
            owner_id=str(current_user_id),
            city_code=request.city_code,
            title=request.title,
            content=request.content,
            idol=request.idol,
            idol_group=request.idol_group,
            expires_at=request.expires_at,
        )

        return PostResponse(
            id=UUID(post.id),
            owner_id=UUID(post.owner_id),
            city_code=post.city_code,
            title=post.title,
            content=post.content,
            idol=post.idol,
            idol_group=post.idol_group,
            status=post.status.value,
            expires_at=post.expires_at,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

    except ValueError as e:
        logger.warning(f"Post creation validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post",
        )


@router.get(
    "",
    response_model=PostListResponse,
    responses={
        200: {"description": "Posts retrieved successfully"},
        400: {"description": "Bad request (city_code required)"},
        500: {"description": "Internal server error"},
    },
    summary="List posts on a city board",
    description="List all open posts for a specific city with optional filters",
)
async def list_posts(
    city_code: Annotated[str, Query(..., description="City code (required)")],
    idol: Annotated[Optional[str], Query(None, description="Filter by idol name")] = None,
    idol_group: Annotated[Optional[str], Query(None, description="Filter by idol group")] = None,
    limit: Annotated[int, Query(50, ge=1, le=100, description="Maximum results")] = 50,
    offset: Annotated[int, Query(0, ge=0, description="Pagination offset")] = 0,
    session: Annotated[AsyncSession, Depends(get_db_session)] = Depends(get_db_session),
) -> PostListResponse:
    """
    List posts for a city board.

    Only shows posts with status=open and not expired.
    Results ordered by created_at DESC (newest first).
    """
    try:
        # Initialize repository and use case
        post_repo = PostRepositoryImpl(session)
        use_case = ListBoardPostsUseCase(post_repo)

        # Execute use case
        posts = await use_case.execute(
            city_code=city_code,
            idol=idol,
            idol_group=idol_group,
            limit=limit,
            offset=offset,
        )

        post_responses = [
            PostResponse(
                id=UUID(post.id),
                owner_id=UUID(post.owner_id),
                city_code=post.city_code,
                title=post.title,
                content=post.content,
                idol=post.idol,
                idol_group=post.idol_group,
                status=post.status.value,
                expires_at=post.expires_at,
                created_at=post.created_at,
                updated_at=post.updated_at,
            )
            for post in posts
        ]

        return PostListResponse(posts=post_responses, total=len(post_responses))

    except ValueError as e:
        logger.warning(f"Post list validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing posts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list posts",
        )


@router.post(
    "/{post_id}/interest",
    response_model=PostInterestResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Interest expressed successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        404: {"description": "Post not found"},
        422: {"description": "Unprocessable entity (validation failed)"},
        500: {"description": "Internal server error"},
    },
    summary="Express interest in a post",
    description="Express interest in a post. Cannot express interest in your own post or duplicate interests.",
)
async def express_interest(
    post_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostInterestResponse:
    """
    Express interest in a post.

    Business rules:
    - Cannot express interest in your own post
    - Cannot express interest twice in the same post
    - Post must be open and not expired
    """
    try:
        # Initialize repositories and use case
        post_repo = PostRepositoryImpl(session)
        interest_repo = PostInterestRepositoryImpl(session)
        use_case = ExpressInterestUseCase(post_repo, interest_repo)

        # Execute use case
        interest = await use_case.execute(
            post_id=str(post_id),
            user_id=str(current_user_id),
        )

        return PostInterestResponse(
            id=UUID(interest.id),
            post_id=UUID(interest.post_id),
            user_id=UUID(interest.user_id),
            status=interest.status.value,
            created_at=interest.created_at,
            updated_at=interest.updated_at,
        )

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        logger.warning(f"Interest validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error expressing interest: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to express interest",
        )


@router.post(
    "/{post_id}/interests/{interest_id}/accept",
    response_model=AcceptInterestResponse,
    responses={
        200: {"description": "Interest accepted successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        403: {"description": "Forbidden (not post owner)"},
        404: {"description": "Post or interest not found"},
        422: {"description": "Unprocessable entity (validation failed)"},
        500: {"description": "Internal server error"},
    },
    summary="Accept an interest",
    description="Accept an interest. Automatically creates friendship and chat room.",
)
async def accept_interest(
    post_id: UUID,
    interest_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AcceptInterestResponse:
    """
    Accept an interest.

    Business rules:
    - Only post owner can accept interests
    - Interest must be pending
    - Automatically creates friendship if not already friends
    - Creates or reuses existing chat room
    """
    try:
        # Initialize repositories and use case
        post_repo = PostRepositoryImpl(session)
        interest_repo = PostInterestRepositoryImpl(session)
        friendship_repo = FriendshipRepositoryImpl(session)
        chat_room_repo = ChatRoomRepositoryImpl(session)
        use_case = AcceptInterestUseCase(
            post_repo, interest_repo, friendship_repo, chat_room_repo
        )

        # Execute use case
        result = await use_case.execute(
            post_id=str(post_id),
            interest_id=str(interest_id),
            current_user_id=str(current_user_id),
        )

        return AcceptInterestResponse(
            interest_id=UUID(result.interest_id),
            friendship_created=result.friendship_created,
            chat_room_id=UUID(result.chat_room_id),
        )

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "only post owner" in error_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        logger.warning(f"Accept interest validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error accepting interest: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept interest",
        )


@router.post(
    "/{post_id}/interests/{interest_id}/reject",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Interest rejected successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        403: {"description": "Forbidden (not post owner)"},
        404: {"description": "Post or interest not found"},
        422: {"description": "Unprocessable entity (validation failed)"},
        500: {"description": "Internal server error"},
    },
    summary="Reject an interest",
    description="Reject an interest. Only post owner can reject.",
)
async def reject_interest(
    post_id: UUID,
    interest_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """
    Reject an interest.

    Business rules:
    - Only post owner can reject interests
    - Interest must be pending
    """
    try:
        # Initialize repositories and use case
        post_repo = PostRepositoryImpl(session)
        interest_repo = PostInterestRepositoryImpl(session)
        use_case = RejectInterestUseCase(post_repo, interest_repo)

        # Execute use case
        await use_case.execute(
            post_id=str(post_id),
            interest_id=str(interest_id),
            current_user_id=str(current_user_id),
        )

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "only post owner" in error_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        logger.warning(f"Reject interest validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error rejecting interest: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject interest",
        )


@router.post(
    "/{post_id}/close",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Post closed successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        403: {"description": "Forbidden (not post owner)"},
        404: {"description": "Post not found"},
        422: {"description": "Unprocessable entity (post not open)"},
        500: {"description": "Internal server error"},
    },
    summary="Close a post",
    description="Manually close a post. Only post owner can close.",
)
async def close_post(
    post_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """
    Close a post manually.

    Business rules:
    - Only post owner can close the post
    - Post must be open
    """
    try:
        # Initialize repository and use case
        post_repo = PostRepositoryImpl(session)
        use_case = ClosePostUseCase(post_repo)

        # Execute use case
        await use_case.execute(
            post_id=str(post_id),
            current_user_id=str(current_user_id),
        )

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "only post owner" in error_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        logger.warning(f"Close post validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error closing post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close post",
        )
