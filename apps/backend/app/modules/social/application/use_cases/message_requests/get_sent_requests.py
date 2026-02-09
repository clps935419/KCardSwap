"""Get Message Requests for Sender Use Case"""

from typing import List

from app.modules.social.domain.entities.message_request import (
    MessageRequest,
    RequestStatus,
)
from app.modules.social.domain.repositories.i_message_request_repository import (
    IMessageRequestRepository,
)


class GetSentMessageRequestsUseCase:
    """
    Use case for getting message requests sent by a user.

    Only pending requests are typically shown to the sender.
    """

    def __init__(
        self,
        message_request_repository: IMessageRequestRepository,
    ):
        self.message_request_repository = message_request_repository

    async def execute(
        self, sender_id: str, status_filter: str = "pending"
    ) -> List[MessageRequest]:
        """
        Get message requests sent by a user.

        Args:
            sender_id: ID of the sender user
            status_filter: Status to filter ("pending", "accepted", "declined", "all")

        Returns:
            List of MessageRequest entities
        """
        status = None
        if status_filter != "all":
            status = RequestStatus(status_filter)

        return await self.message_request_repository.get_requests_for_sender(
            sender_id, status
        )
