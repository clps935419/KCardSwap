"""Decline Message Request Use Case"""

from app.modules.social.domain.entities.message_request import MessageRequest
from app.modules.social.domain.repositories.i_message_request_repository import (
    IMessageRequestRepository,
)


class DeclineMessageRequestUseCase:
    """
    Use case for declining a message request.

    Implements FR-012: Recipient can accept/decline requests.
    """

    def __init__(
        self,
        message_request_repository: IMessageRequestRepository,
    ):
        self.message_request_repository = message_request_repository

    async def execute(
        self, request_id: str, declining_user_id: str
    ) -> MessageRequest:
        """
        Decline a message request.

        Args:
            request_id: ID of the message request
            declining_user_id: ID of user declining (must be recipient)

        Returns:
            Updated MessageRequest entity

        Raises:
            ValueError: If request not found, not recipient, or already processed
        """
        # Get request
        message_request = await self.message_request_repository.get_by_id(request_id)
        if not message_request:
            raise ValueError("Message request not found")

        # Verify declining user is the recipient
        if message_request.recipient_id != declining_user_id:
            raise ValueError("Only the recipient can decline this request")

        # Verify request is pending
        if not message_request.is_pending():
            raise ValueError(
                f"Cannot decline request with status {message_request.status}"
            )

        # Decline request
        message_request.decline()
        return await self.message_request_repository.update(message_request)
