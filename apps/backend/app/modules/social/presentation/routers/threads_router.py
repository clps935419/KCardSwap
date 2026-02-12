"""Threads Router - API endpoints for message threads"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.infrastructure.repositories.profile_repository_impl import (
    ProfileRepositoryImpl,
)
from app.modules.social.application.use_cases.messages.get_messages import (
    GetThreadMessagesUseCase,
)
from app.modules.social.application.use_cases.messages.get_threads import (
    GetThreadsUseCase,
)
from app.modules.social.application.use_cases.messages.send_message import (
    SendMessageUseCase,
)
from app.modules.social.infrastructure.repositories.thread_message_repository import (
    ThreadMessageRepository,
)
from app.modules.social.infrastructure.repositories.thread_repository import (
    ThreadRepository,
)
from app.modules.social.presentation.schemas.message_schemas import (
    SendMessageRequest,
    ThreadListResponse,
    ThreadListResponseWrapper,
    ThreadMessageResponse,
    ThreadMessageResponseWrapper,
    ThreadMessagesResponse,
    ThreadMessagesResponseWrapper,
    ThreadResponse,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import require_user

router = APIRouter(prefix="/threads", tags=["threads"])


async def _get_user_profile_data(user_id: str, profile_repo: ProfileRepositoryImpl):
    """Helper to fetch nickname and avatar_url for a user"""
    try:
        profile = await profile_repo.get_by_user_id(UUID(user_id))
        if profile:
            return profile.nickname, profile.avatar_url
    except Exception:
        pass
    return None, None


@router.get("", response_model=ThreadListResponseWrapper)
async def get_my_threads(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: UUID = Depends(require_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get all threads for the current user.

    Supports FR-016: Inbox clearly separates Requests vs Threads.
    Returns threads ordered by last_message_at descending.
    """
    thread_repo = ThreadRepository(session)
    profile_repo = ProfileRepositoryImpl(session)
    use_case = GetThreadsUseCase(thread_repo)

    threads = await use_case.execute(
        user_id=str(user_id), limit=limit, offset=offset
    )

    # Build response list with profile data
    thread_responses = []
    for thread in threads:
        user_a_nickname, user_a_avatar_url = await _get_user_profile_data(
            thread.user_a_id, profile_repo
        )
        user_b_nickname, user_b_avatar_url = await _get_user_profile_data(
            thread.user_b_id, profile_repo
        )
        thread_responses.append(
            ThreadResponse(
                id=thread.id,
                user_a_id=thread.user_a_id,
                user_a_nickname=user_a_nickname,
                user_a_avatar_url=user_a_avatar_url,
                user_b_id=thread.user_b_id,
                user_b_nickname=user_b_nickname,
                user_b_avatar_url=user_b_avatar_url,
                created_at=thread.created_at,
                updated_at=thread.updated_at,
                last_message_at=thread.last_message_at,
            )
        )

    return {
        "data": ThreadListResponse(
            threads=thread_responses,
            total=len(thread_responses),
        ),
        "meta": None,
        "error": None,
    }


@router.get("/{thread_id}/messages", response_model=ThreadMessagesResponseWrapper)
async def get_thread_messages(
    thread_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: UUID = Depends(require_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get messages in a thread.

    Returns messages ordered by created_at ascending (oldest first).
    User must be part of the thread to view messages.
    """
    thread_repo = ThreadRepository(session)
    thread_message_repo = ThreadMessageRepository(session)
    profile_repo = ProfileRepositoryImpl(session)

    use_case = GetThreadMessagesUseCase(thread_repo, thread_message_repo)

    try:
        messages = await use_case.execute(
            thread_id=thread_id,
            user_id=str(user_id),
            limit=limit,
            offset=offset,
        )

        # Build response list with profile data
        message_responses = []
        for msg in messages:
            sender_nickname, sender_avatar_url = await _get_user_profile_data(
                msg.sender_id, profile_repo
            )
            message_responses.append(
                ThreadMessageResponse(
                    id=msg.id,
                    thread_id=msg.thread_id,
                    sender_id=msg.sender_id,
                    sender_nickname=sender_nickname,
                    sender_avatar_url=sender_avatar_url,
                    content=msg.content,
                    post_id=msg.post_id,
                    created_at=msg.created_at,
                )
            )

        return {
            "data": ThreadMessagesResponse(
                messages=message_responses,
                total=len(message_responses),
            ),
            "meta": None,
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{thread_id}/messages", response_model=ThreadMessageResponseWrapper, status_code=status.HTTP_201_CREATED)
async def send_message(
    thread_id: str,
    request: SendMessageRequest,
    user_id: UUID = Depends(require_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Send a message in a thread.

    Supports FR-015: Messages can reference post_id.
    User must be part of the thread to send messages.
    """
    thread_repo = ThreadRepository(session)
    thread_message_repo = ThreadMessageRepository(session)
    profile_repo = ProfileRepositoryImpl(session)

    use_case = SendMessageUseCase(thread_repo, thread_message_repo)

    try:
        message = await use_case.execute(
            thread_id=thread_id,
            sender_id=str(user_id),
            content=request.content,
            post_id=request.post_id,
        )

        # Fetch profile data for sender
        sender_nickname, sender_avatar_url = await _get_user_profile_data(
            message.sender_id, profile_repo
        )

        return {
            "data": ThreadMessageResponse(
                id=message.id,
                thread_id=message.thread_id,
                sender_id=message.sender_id,
                sender_nickname=sender_nickname,
                sender_avatar_url=sender_avatar_url,
                content=message.content,
                post_id=message.post_id,
                created_at=message.created_at,
            ),
            "meta": None,
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
