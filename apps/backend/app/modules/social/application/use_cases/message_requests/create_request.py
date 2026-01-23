"""Create Message Request Use Case"""

import uuid
from datetime import datetime
from typing import Optional

from app.modules.social.domain.entities.message_request import (
    MessageRequest,
    RequestStatus,
)
from app.modules.social.domain.repositories.i_friendship_repository import (
    IFriendshipRepository,
)
from app.modules.social.domain.repositories.i_message_request_repository import (
    IMessageRequestRepository,
)
from app.modules.social.application.services.thread_uniqueness_service import (
    ThreadUniquenessService,
)


class CreateMessageRequestUseCase:
    """
    Use case for creating a message request from a stranger.
    
    Implements FR-011: Message Requests for strangers.
    Implements FR-013: Privacy setting to block stranger messages.
    Implements FR-014: One unique thread per user pair.
    """

    def __init__(
        self,
        message_request_repository: IMessageRequestRepository,
        friendship_repository: IFriendshipRepository,
        thread_uniqueness_service: ThreadUniquenessService,
    ):
        self.message_request_repository = message_request_repository
        self.friendship_repository = friendship_repository
        self.thread_uniqueness_service = thread_uniqueness_service

    async def execute(
        self,
        sender_id: str,
        recipient_id: str,
        initial_message: str,
        post_id: Optional[str] = None,
        recipient_allows_stranger_messages: bool = True,
    ) -> MessageRequest:
        """
        Create a message request from sender to recipient.
        
        Args:
            sender_id: ID of user sending the request
            recipient_id: ID of user receiving the request
            initial_message: Initial message content
            post_id: Optional post ID being referenced
            recipient_allows_stranger_messages: Privacy setting from recipient
        
        Returns:
            Created MessageRequest entity
        
        Raises:
            ValueError: If request is invalid
        """
        # Validate: cannot message yourself
        if sender_id == recipient_id:
            raise ValueError("Cannot send message request to yourself")

        # Check privacy: recipient must allow stranger messages (FR-013)
        if not recipient_allows_stranger_messages:
            # Check if they're friends first
            are_friends = await self.friendship_repository.are_friends(
                sender_id, recipient_id
            )
            if not are_friends:
                raise ValueError(
                    "Recipient does not accept messages from strangers"
                )

        # Check blocking (FR-025)
        is_blocked = await self.friendship_repository.is_blocked(sender_id, recipient_id)
        if is_blocked:
            raise ValueError("Cannot send message request - you are blocked by this user")

        # Check reverse blocking
        is_sender_blocking = await self.friendship_repository.is_blocked(
            recipient_id, sender_id
        )
        if is_sender_blocking:
            raise ValueError("Cannot send message request - you have blocked this user")

        # Check uniqueness: no existing thread or pending request (FR-014)
        existing_thread, pending_request = (
            await self.thread_uniqueness_service.find_or_get_pending_request(
                sender_id, recipient_id
            )
        )

        if existing_thread:
            raise ValueError(
                "Thread already exists with this user. "
                "Use the existing thread to send messages."
            )

        if pending_request:
            raise ValueError(
                "Message request already pending with this user"
            )

        # Create message request
        message_request = MessageRequest(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            initial_message=initial_message,
            post_id=post_id,
            status=RequestStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        return await self.message_request_repository.create(message_request)
