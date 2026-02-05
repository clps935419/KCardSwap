"""
Posts Router for Posts Module
Handles city board posts and interest management (V2: with scope/category/require_user)
"""

import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.application.use_cases.close_post_use_case import ClosePostUseCase
from app.modules.posts.application.use_cases.create_post_use_case import (
    CreatePostUseCase,
)
from app.modules.posts.application.use_cases.list_posts_v2_use_case import (
    ListPostsV2UseCase,
)
from app.modules.posts.application.use_cases.toggle_like import ToggleLikeUseCase
from app.modules.posts.domain.entities.post_enums import PostCategory
from app.modules.posts.presentation.dependencies.use_case_deps import (
    get_close_post_use_case,
    get_create_post_use_case,
    get_list_posts_v2_use_case,
    get_toggle_like_use_case,
)
from app.modules.posts.presentation.schemas.post_schemas import (
    CreatePostRequest,
    PostListResponse,
    PostListResponseWrapper,
    PostResponse,
    PostResponseWrapper,
    ToggleLikeResponse,
    ToggleLikeResponseWrapper,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import require_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/posts", tags=["Posts"])


def _post_to_response(post, like_count: int = 0, liked_by_me: bool = False) -> PostResponse:
    """Helper to convert Post entity to PostResponse"""
    return PostResponse(
        id=UUID(post.id),
        owner_id=UUID(post.owner_id),
        scope=post.scope.value,
        city_code=post.city_code,
        category=post.category.value,
        title=post.title,
        content=post.content,
        idol=post.idol,
        idol_group=post.idol_group,
        status=post.status.value,
        like_count=like_count,
        liked_by_me=liked_by_me,
        expires_at=post.expires_at,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.post(
    "",
    response_model=PostResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Post created successfully"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        422: {
            "description": "Unprocessable entity (daily limit exceeded or validation failed)"
        },
        500: {"description": "Internal server error"},
    },
    summary="Create a new post (V2: with scope/category)",
    description="Create a new post. Requires authentication. Free users limited to 2 posts per day, Premium to 20.",
)
async def create_post(
    request: CreatePostRequest,
    current_user_id: Annotated[UUID, Depends(require_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[CreatePostUseCase, Depends(get_create_post_use_case)],
) -> PostResponseWrapper:
    """
    Create a new post (V2: with scope/category).

    Business rules (FR-003, FR-004, FR-023):
    - Free users: 2 posts per day
    - Premium users: 20 posts per day
    - Posts expire after 14 days by default
    - scope=city requires city_code
    - scope=global must not have city_code
    """
    try:
        post = await use_case.execute(
            owner_id=str(current_user_id),
            scope=request.scope,
            category=request.category,
            city_code=request.city_code,
            title=request.title,
            content=request.content,
            idol=request.idol,
            idol_group=request.idol_group,
            expires_at=request.expires_at,
        )

        data = _post_to_response(post)
        return PostResponseWrapper(data=data, meta=None, error=None)

    except ValueError as e:
        logger.warning(f"Post creation validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post",
        )


@router.get(
    "",
    response_model=PostListResponseWrapper,
    responses={
        200: {"description": "Posts retrieved successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
    summary="List posts (V2: global/city filtering with category)",
    description="List posts. FR-005: Global view (no city_code) shows all posts; City view (with city_code) shows city-specific posts.",
)
async def list_posts(
    current_user_id: Annotated[UUID, Depends(require_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[ListPostsV2UseCase, Depends(get_list_posts_v2_use_case)],
    city_code: Annotated[Optional[str], Query(description="Optional city filter (omit for global view)")] = None,
    category: Annotated[Optional[PostCategory], Query(description="Optional category filter")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum results")] = 50,
    offset: Annotated[int, Query(ge=0, description="Pagination offset")] = 0,
) -> PostListResponseWrapper:
    """
    List posts (V2: supports global/city filtering).

    FR-005:
    - Global view (city_code=None): shows all posts (scope=global + scope=city)
    - City view (city_code provided): shows only posts for that city

    Only shows posts with status=open and not expired.
    Results ordered by created_at DESC (newest first).
    """
    try:
        posts_with_likes = await use_case.execute(
            current_user_id=str(current_user_id),
            city_code=city_code,
            category=category,
            limit=limit,
            offset=offset,
        )

        post_responses = [
            _post_to_response(
                pwl.post,
                like_count=pwl.like_count,
                liked_by_me=pwl.liked_by_me,
            )
            for pwl in posts_with_likes
        ]

        data = PostListResponse(posts=post_responses, total=len(post_responses))
        return PostListResponseWrapper(data=data, meta=None, error=None)

    except ValueError as e:
        logger.warning(f"Post list validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing posts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list posts",
        )


# REMOVED: Post interest endpoints - not required for POC
# The following 5 endpoints have been commented out:
# - express_interest, accept_interest, reject_interest, list_post_interests, get_post_interest

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
    current_user_id: Annotated[UUID, Depends(require_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[ClosePostUseCase, Depends(get_close_post_use_case)],
) -> None:
    """
    Close a post manually.

    Business rules:
    - Only post owner can close the post
    - Post must be open
    """
    try:
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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error closing post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close post",
        )


@router.post(
    "/{post_id}/like",
    response_model=ToggleLikeResponseWrapper,
    responses={
        200: {"description": "Like toggled successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        404: {"description": "Post not found"},
        500: {"description": "Internal server error"},
    },
    summary="Toggle like on a post (FR-008, FR-009)",
    description="Like or unlike a post. Idempotent: if already liked, unlikes; if not liked, likes. Each user can like a post at most once.",
)
async def toggle_like(
    post_id: UUID,
    current_user_id: Annotated[UUID, Depends(require_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[ToggleLikeUseCase, Depends(get_toggle_like_use_case)],
) -> ToggleLikeResponseWrapper:
    """
    Toggle like on a post (FR-008, FR-009).

    Idempotent operation:
    - If user has already liked the post, this will unlike it
    - If user has not liked the post, this will like it

    Returns the new like state (liked/unliked) and the current total like count.
    """
    try:
        result = await use_case.execute(
            post_id=str(post_id),
            user_id=str(current_user_id),
        )

        data = ToggleLikeResponse(
            liked=result.liked,
            like_count=result.like_count,
        )
        return ToggleLikeResponseWrapper(data=data, meta=None, error=None)

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error toggling like on post {post_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle like",
        )
