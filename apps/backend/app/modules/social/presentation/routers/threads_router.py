"""Threads Router - API endpoints for message threads"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

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
    ThreadMessageResponse,
    ThreadMessagesResponse,
    ThreadResponse,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.deps.require_user import require_user

router = APIRouter(prefix="/threads", tags=["threads"])


@router.get("", response_model=ThreadListResponse)
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
    use_case = GetThreadsUseCase(thread_repo)

    threads = await use_case.execute(
        user_id=str(user_id), limit=limit, offset=offset
    )

    return ThreadListResponse(
        threads=[
            ThreadResponse(
                id=thread.id,
                user_a_id=thread.user_a_id,
                user_b_id=thread.user_b_id,
                created_at=thread.created_at,
                updated_at=thread.updated_at,
                last_message_at=thread.last_message_at,
            )
            for thread in threads
        ],
        total=len(threads),
    )


@router.get("/{thread_id}/messages", response_model=ThreadMessagesResponse)
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

    use_case = GetThreadMessagesUseCase(thread_repo, thread_message_repo)

    try:
        messages = await use_case.execute(
            thread_id=thread_id,
            user_id=str(user_id),
            limit=limit,
            offset=offset,
        )

        return ThreadMessagesResponse(
            messages=[
                ThreadMessageResponse(
                    id=msg.id,
                    thread_id=msg.thread_id,
                    sender_id=msg.sender_id,
                    content=msg.content,
                    post_id=msg.post_id,
                    created_at=msg.created_at,
                )
                for msg in messages
            ],
            total=len(messages),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{thread_id}/messages", response_model=ThreadMessageResponse, status_code=status.HTTP_201_CREATED)
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

    use_case = SendMessageUseCase(thread_repo, thread_message_repo)

    try:
        message = await use_case.execute(
            thread_id=thread_id,
            sender_id=str(user_id),
            content=request.content,
            post_id=request.post_id,
        )

        return ThreadMessageResponse(
            id=message.id,
            thread_id=message.thread_id,
            sender_id=message.sender_id,
            content=message.content,
            post_id=message.post_id,
            created_at=message.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
