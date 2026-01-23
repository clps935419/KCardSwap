"""Get Message Requests for Recipient Use Case"""

from typing import List

from app.modules.social.domain.entities.message_request import (
    MessageRequest,
    RequestStatus,
)
from app.modules.social.domain.repositories.i_message_request_repository import (
    IMessageRequestRepository,
)


class GetMessageRequestsUseCase:
    """
    Use case for getting message requests for a recipient.
    
    Supports FR-016: Inbox clearly separates Requests vs Threads.
    """

    def __init__(
        self,
        message_request_repository: IMessageRequestRepository,
    ):
        self.message_request_repository = message_request_repository

    async def execute(
        self, recipient_id: str, status_filter: str = "pending"
    ) -> List[MessageRequest]:
        """
        Get message requests for a recipient.
        
        Args:
            recipient_id: ID of the recipient user
            status_filter: Status to filter ("pending", "accepted", "declined", "all")
        
        Returns:
            List of MessageRequest entities
        """
        status = None
        if status_filter != "all":
            status = RequestStatus(status_filter)

        return await self.message_request_repository.get_requests_for_recipient(
            recipient_id, status
        )
