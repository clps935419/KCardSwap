"""
Chat Router for Social Module
Handles chat rooms, messages, and FCM push notifications
"""

import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.application.use_cases.chat.get_messages_use_case import (
    GetMessagesUseCase,
)
from app.modules.social.application.use_cases.chat.send_message_use_case import (
    SendMessageUseCase,
)
from app.modules.social.domain.entities.message import MessageStatus
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.message_repository_impl import (
    MessageRepositoryImpl,
)
from app.modules.social.presentation.schemas.chat_schemas import (
    ChatRoomListResponse,
    ChatRoomListResponseWrapper,
    ChatRoomResponse,
    MessageResponse,
    MessageResponseWrapper,
    MessagesListResponse,
    MessagesListResponseWrapper,
    SendMessageRequest,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.infrastructure.external.fcm_service import get_fcm_service
from app.shared.presentation.dependencies.auth import get_current_user_id

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chats", tags=["Chat"])


@router.get(
    "",
    response_model=ChatRoomListResponseWrapper,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Chat rooms retrieved successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        500: {"description": "Internal server error"},
    },
    summary="Get chat rooms",
    description="Get all chat rooms for the current user",
)
async def get_chat_rooms(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatRoomListResponseWrapper:
    """
    Get all chat rooms for the current user.

    Returns a list of chat rooms with:
    - Room details
    - Participants
    - Last message
    - Unread count (placeholder)
    """
    try:
        # Initialize repository
        chat_room_repo = ChatRoomRepositoryImpl(session)

        # Get chat rooms for user
        chat_rooms = await chat_room_repo.get_rooms_by_user_id(str(current_user_id))

        # Convert to response format
        # Note: In a real implementation, we would fetch:
        # - User profiles for participants
        # - Last message for each room
        # - Unread count
        from app.modules.social.presentation.schemas.chat_schemas import (
            ChatRoomParticipantResponse,
        )

        room_responses = []
        for room in chat_rooms:
            participants = [
                ChatRoomParticipantResponse(
                    user_id=UUID(uid),
                    nickname=None,  # TODO: Fetch from profile
                    avatar_url=None,  # TODO: Fetch from profile
                )
                for uid in room.participant_ids
            ]

            room_responses.append(
                ChatRoomResponse(
                    id=UUID(room.id),
                    participants=participants,
                    last_message=None,  # TODO: Fetch last message
                    unread_count=0,  # TODO: Calculate unread count
                    created_at=room.created_at,
                )
            )

        data = ChatRoomListResponse(rooms=room_responses, total=len(room_responses))
        return ChatRoomListResponseWrapper(data=data, meta=None, error=None)

    except Exception as e:
        logger.error(f"Error getting chat rooms: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat rooms",
        )


@router.get(
    "/{room_id}/messages",
    response_model=MessagesListResponseWrapper,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Messages retrieved successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        403: {"description": "Forbidden (not a participant of this room)"},
        404: {"description": "Chat room not found"},
        500: {"description": "Internal server error"},
    },
    summary="Get messages",
    description="Get messages from a chat room (with pagination support via after_message_id)",
)
async def get_messages(
    room_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    after_message_id: Optional[UUID] = Query(
        None, description="Get messages after this message ID"
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages"),
) -> MessagesListResponseWrapper:
    """
    Get messages from a chat room.

    Supports pagination via after_message_id for polling:
    - Pass after_message_id to get only new messages since that ID
    - Useful for implementing polling mechanism in client
    """
    try:
        # Initialize repositories and use case
        message_repo = MessageRepositoryImpl(session)
        chat_room_repo = ChatRoomRepositoryImpl(session)
        friendship_repo = FriendshipRepositoryImpl(session)
        use_case = GetMessagesUseCase(message_repo, chat_room_repo, friendship_repo)

        # Execute use case
        messages = await use_case.execute(
            room_id=str(room_id),
            requesting_user_id=str(current_user_id),
            after_message_id=str(after_message_id) if after_message_id else None,
            limit=limit,
        )

        # Convert to response format
        message_responses = [
            MessageResponse(
                id=UUID(msg.id),
                room_id=UUID(msg.room_id),
                sender_id=UUID(msg.sender_id),
                content=msg.content,
                status=msg.status.value,
                created_at=msg.created_at,
            )
            for msg in messages
        ]

        data = MessagesListResponse(
            messages=message_responses,
            total=len(message_responses),
            has_more=len(messages)
            == limit,  # If we got exactly limit, there might be more
        )

        return MessagesListResponseWrapper(data=data, meta=None, error=None)

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "not a participant" in error_msg or "not authorized" in error_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
    except Exception as e:
        logger.error(f"Error getting messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get messages",
        )


@router.post(
    "/{room_id}/messages",
    response_model=MessageResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Message sent successfully"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        403: {"description": "Forbidden (not authorized to send message)"},
        404: {"description": "Chat room not found"},
        422: {"description": "Unprocessable entity (blocked or not friends)"},
        500: {"description": "Internal server error"},
    },
    summary="Send message",
    description="Send a message in a chat room (triggers FCM push notification)",
)
async def send_message(
    room_id: UUID,
    request: SendMessageRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageResponseWrapper:
    """
    Send a message in a chat room.

    Business rules:
    - Users must be friends
    - Users must not be blocked
    - Sender must be a participant in the room

    After successful message creation:
    - Triggers FCM push notification to recipient
    - Notification failure does not fail the request
    """
    try:
        # Initialize repositories and use case
        message_repo = MessageRepositoryImpl(session)
        chat_room_repo = ChatRoomRepositoryImpl(session)
        friendship_repo = FriendshipRepositoryImpl(session)

        use_case = SendMessageUseCase(message_repo, chat_room_repo, friendship_repo)

        # Execute use case
        message = await use_case.execute(
            room_id=str(room_id),
            sender_id=str(current_user_id),
            content=request.content,
        )

        # Convert to response
        data = MessageResponse(
            id=UUID(message.id),
            room_id=UUID(message.room_id),
            sender_id=UUID(message.sender_id),
            content=message.content,
            status=message.status.value,
            created_at=message.created_at,
        )

        # Send FCM push notification (non-blocking, failures are logged)
        try:
            fcm_service = get_fcm_service()

            # Get chat room to find recipient
            chat_room = await chat_room_repo.get_by_id(str(room_id))
            if chat_room:
                recipient_id = chat_room.get_other_participant(str(current_user_id))

                # Send notification
                # Note: In production, we would fetch FCM token from user profile
                await fcm_service.send_notification(
                    user_id=recipient_id,
                    title="New message",
                    body=message.content[:50]
                    + ("..." if len(message.content) > 50 else ""),
                    data={
                        "type": "chat_message",
                        "room_id": str(room_id),
                        "message_id": str(message.id),
                    },
                    fcm_token=None,  # TODO: Fetch from user profile
                )
        except Exception as e:
            # Log but don't fail the request
            logger.warning(f"Failed to send FCM notification: {e}")

        return MessageResponseWrapper(data=data, meta=None, error=None)

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "not authorized" in error_msg or "not a participant" in error_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
    except Exception as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )


@router.post(
    "/{room_id}/messages/{message_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Message marked as read"},
        401: {"description": "Unauthorized (not logged in)"},
        403: {"description": "Forbidden (not authorized)"},
        404: {"description": "Message not found"},
        500: {"description": "Internal server error"},
    },
    summary="Mark message as read",
    description="Mark a message as read by the current user",
)
async def mark_message_read(
    room_id: UUID,
    message_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """
    Mark a message as read.

    Business rules:
    - User must be a participant in the room
    - User cannot mark their own messages as read
    - Only unread messages (SENT or DELIVERED) will be marked as READ
    - Already read messages return success without changes
    """
    try:
        # Initialize repositories
        message_repo = MessageRepositoryImpl(session)
        chat_room_repo = ChatRoomRepositoryImpl(session)

        # Verify room exists and user is participant
        chat_room = await chat_room_repo.get_by_id(str(room_id))
        if not chat_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found"
            )

        if not chat_room.has_participant(str(current_user_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this chat room",
            )

        # Verify message exists
        message = await message_repo.get_by_id(str(message_id))
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
            )

        # Cannot mark own message as read
        if message.sender_id == str(current_user_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot mark your own message as read",
            )

        # Only mark if message is not already read
        if message.status == MessageStatus.READ:
            # Already read, just return success
            return

        # Mark message as read using entity method
        message.mark_read()

        # Update message in database
        await message_repo.update(message)

        logger.info(f"Message {message_id} marked as read by {current_user_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking message as read: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark message as read",
        )
