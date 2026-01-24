"""
MessageRequest Repository Interface

Domain layer repository interface - defines contract for message request persistence
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.social.domain.entities.message_request import MessageRequest, RequestStatus


class IMessageRequestRepository(ABC):
    """Repository interface for MessageRequest entity persistence"""

    @abstractmethod
    async def create(self, message_request: MessageRequest) -> MessageRequest:
        """Create a new message request"""
        pass

    @abstractmethod
    async def get_by_id(self, request_id: str) -> Optional[MessageRequest]:
        """Get message request by ID"""
        pass

    @abstractmethod
    async def find_pending_between_users(
        self, user_a_id: str, user_b_id: str
    ) -> Optional[MessageRequest]:
        """
        Find pending message request between two users (either direction)
        
        Returns the pending request if exists, None otherwise.
        """
        pass

    @abstractmethod
    async def get_requests_for_recipient(
        self, recipient_id: str, status: Optional[RequestStatus] = None
    ) -> List[MessageRequest]:
        """
        Get all message requests for a recipient
        
        Args:
            recipient_id: ID of the recipient user
            status: Optional status filter (PENDING, ACCEPTED, DECLINED)
        
        Returns:
            List of message requests ordered by created_at descending
        """
        pass

    @abstractmethod
    async def update(self, message_request: MessageRequest) -> MessageRequest:
        """Update an existing message request"""
        pass

    @abstractmethod
    async def delete(self, request_id: str) -> None:
        """Delete a message request"""
        pass
