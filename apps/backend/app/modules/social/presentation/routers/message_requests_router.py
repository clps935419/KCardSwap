"""Message Requests Router - API endpoints for message requests"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.infrastructure.database.session import get_db_session
from app.shared.presentation.deps.require_user import require_user
from app.modules.social.application.use_cases.message_requests.create_request import (
    CreateMessageRequestUseCase,
)
from app.modules.social.application.use_cases.message_requests.accept_request import (
    AcceptMessageRequestUseCase,
)
from app.modules.social.application.use_cases.message_requests.decline_request import (
    DeclineMessageRequestUseCase,
)
from app.modules.social.application.use_cases.message_requests.get_requests import (
    GetMessageRequestsUseCase,
)
from app.modules.social.application.services.thread_uniqueness_service import (
    ThreadUniquenessService,
)
from app.modules.social.infrastructure.repositories.message_request_repository import (
    MessageRequestRepository,
)
from app.modules.social.infrastructure.repositories.thread_repository import (
    ThreadRepository,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)
from app.modules.identity.infrastructure.repositories.profile_repository_impl import (
    ProfileRepositoryImpl,
)
from app.modules.social.presentation.schemas.message_schemas import (
    CreateMessageRequestRequest,
    MessageRequestResponse,
    AcceptRequestResponse,
    ThreadResponse,
)

router = APIRouter(prefix="/api/v1/message-requests", tags=["message-requests"])


@router.post("", response_model=MessageRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_message_request(
    request: CreateMessageRequestRequest,
    user_id: UUID = Depends(require_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Create a message request to another user.
    
    Implements FR-011: Message Requests for strangers.
    Implements FR-013: Privacy setting to block stranger messages.
    Implements FR-014: One unique thread per user pair.
    """
    message_request_repo = MessageRequestRepository(session)
    thread_repo = ThreadRepository(session)
    friendship_repo = FriendshipRepositoryImpl(session)
    profile_repo = ProfileRepositoryImpl(session)
    
    thread_uniqueness_service = ThreadUniquenessService(
        thread_repo, message_request_repo
    )
    
    use_case = CreateMessageRequestUseCase(
        message_request_repo, friendship_repo, thread_uniqueness_service
    )
    
    try:
        # Get recipient's privacy settings (FR-013)
        from uuid import UUID as UUIDClass
        recipient_profile = await profile_repo.get_by_user_id(
            UUIDClass(request.recipient_id)
        )
        recipient_allows_stranger_messages = True
        if recipient_profile and recipient_profile.privacy_flags:
            recipient_allows_stranger_messages = recipient_profile.privacy_flags.get(
                "allow_stranger_chat", True
            )
        
        message_request = await use_case.execute(
            sender_id=str(user_id),
            recipient_id=request.recipient_id,
            initial_message=request.initial_message,
            post_id=request.post_id,
            recipient_allows_stranger_messages=recipient_allows_stranger_messages,
        )
        
        return MessageRequestResponse(
            id=message_request.id,
            sender_id=message_request.sender_id,
            recipient_id=message_request.recipient_id,
            initial_message=message_request.initial_message,
            post_id=message_request.post_id,
            status=message_request.status.value,
            thread_id=message_request.thread_id,
            created_at=message_request.created_at,
            updated_at=message_request.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/inbox", response_model=list[MessageRequestResponse])
async def get_my_message_requests(
    status_filter: str = "pending",
    user_id: UUID = Depends(require_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get message requests for the current user.
    
    Supports FR-016: Inbox clearly separates Requests vs Threads.
    
    Query params:
    - status_filter: "pending", "accepted", "declined", or "all" (default: "pending")
    """
    message_request_repo = MessageRequestRepository(session)
    use_case = GetMessageRequestsUseCase(message_request_repo)
    
    try:
        requests = await use_case.execute(
            recipient_id=str(user_id), status_filter=status_filter
        )
        
        return [
            MessageRequestResponse(
                id=req.id,
                sender_id=req.sender_id,
                recipient_id=req.recipient_id,
                initial_message=req.initial_message,
                post_id=req.post_id,
                status=req.status.value,
                thread_id=req.thread_id,
                created_at=req.created_at,
                updated_at=req.updated_at,
            )
            for req in requests
        ]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{request_id}/accept", response_model=AcceptRequestResponse)
async def accept_message_request(
    request_id: str,
    user_id: UUID = Depends(require_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Accept a message request and create a thread.
    
    Implements FR-012: Recipient can accept/decline requests.
    Creates unique thread (FR-014).
    """
    message_request_repo = MessageRequestRepository(session)
    thread_repo = ThreadRepository(session)
    
    use_case = AcceptMessageRequestUseCase(message_request_repo, thread_repo)
    
    try:
        updated_request, thread = await use_case.execute(
            request_id=request_id, accepting_user_id=str(user_id)
        )
        
        return AcceptRequestResponse(
            message_request=MessageRequestResponse(
                id=updated_request.id,
                sender_id=updated_request.sender_id,
                recipient_id=updated_request.recipient_id,
                initial_message=updated_request.initial_message,
                post_id=updated_request.post_id,
                status=updated_request.status.value,
                thread_id=updated_request.thread_id,
                created_at=updated_request.created_at,
                updated_at=updated_request.updated_at,
            ),
            thread=ThreadResponse(
                id=thread.id,
                user_a_id=thread.user_a_id,
                user_b_id=thread.user_b_id,
                created_at=thread.created_at,
                updated_at=thread.updated_at,
                last_message_at=thread.last_message_at,
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{request_id}/decline", response_model=MessageRequestResponse)
async def decline_message_request(
    request_id: str,
    user_id: UUID = Depends(require_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Decline a message request.
    
    Implements FR-012: Recipient can accept/decline requests.
    """
    message_request_repo = MessageRequestRepository(session)
    use_case = DeclineMessageRequestUseCase(message_request_repo)
    
    try:
        updated_request = await use_case.execute(
            request_id=request_id, declining_user_id=str(user_id)
        )
        
        return MessageRequestResponse(
            id=updated_request.id,
            sender_id=updated_request.sender_id,
            recipient_id=updated_request.recipient_id,
            initial_message=updated_request.initial_message,
            post_id=updated_request.post_id,
            status=updated_request.status.value,
            thread_id=updated_request.thread_id,
            created_at=updated_request.created_at,
            updated_at=updated_request.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
