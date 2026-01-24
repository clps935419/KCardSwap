"""Accept Message Request Use Case"""

import uuid
from datetime import datetime

from app.modules.social.domain.entities.thread import MessageThread
from app.modules.social.domain.repositories.i_message_request_repository import (
    IMessageRequestRepository,
)
from app.modules.social.domain.repositories.i_thread_repository import IThreadRepository


class AcceptMessageRequestUseCase:
    """
    Use case for accepting a message request.
    
    Implements FR-012: Recipient can accept/decline requests.
    Creates a unique thread when accepted (FR-014).
    """

    def __init__(
        self,
        message_request_repository: IMessageRequestRepository,
        thread_repository: IThreadRepository,
    ):
        self.message_request_repository = message_request_repository
        self.thread_repository = thread_repository

    async def execute(
        self, request_id: str, accepting_user_id: str
    ) -> tuple[object, MessageThread]:
        """
        Accept a message request and create thread.
        
        Args:
            request_id: ID of the message request
            accepting_user_id: ID of user accepting (must be recipient)
        
        Returns:
            tuple: (updated_request, created_thread)
        
        Raises:
            ValueError: If request not found, not recipient, or already processed
        """
        # Get request
        message_request = await self.message_request_repository.get_by_id(request_id)
        if not message_request:
            raise ValueError("Message request not found")

        # Verify accepting user is the recipient
        if message_request.recipient_id != accepting_user_id:
            raise ValueError("Only the recipient can accept this request")

        # Verify request is pending
        if not message_request.is_pending():
            raise ValueError(
                f"Cannot accept request with status {message_request.status}"
            )

        # Check if thread already exists (edge case: concurrent accept)
        existing_thread = await self.thread_repository.find_by_users(
            message_request.sender_id, message_request.recipient_id
        )
        
        if existing_thread:
            # Thread already exists, just update request
            message_request.accept(existing_thread.id)
            updated_request = await self.message_request_repository.update(
                message_request
            )
            return (updated_request, existing_thread)

        # Create new thread
        thread_id = str(uuid.uuid4())
        
        # Normalize user order for thread (smaller UUID first)
        user_a_id = message_request.sender_id
        user_b_id = message_request.recipient_id
        if user_a_id > user_b_id:
            user_a_id, user_b_id = user_b_id, user_a_id

        thread = MessageThread(
            id=thread_id,
            user_a_id=user_a_id,
            user_b_id=user_b_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_message_at=None,
        )
        created_thread = await self.thread_repository.create(thread)

        # Update request status
        message_request.accept(thread_id)
        updated_request = await self.message_request_repository.update(message_request)

        return (updated_request, created_thread)
