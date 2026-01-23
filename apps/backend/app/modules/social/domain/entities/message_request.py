"""
MessageRequest Entity - Represents a pending message request from a stranger

Domain Entity following DDD principles - framework independent
"""

from datetime import datetime
from enum import Enum
from typing import Optional


class RequestStatus(str, Enum):
    """Message request status enumeration"""

    PENDING = "pending"  # Request sent, awaiting response
    ACCEPTED = "accepted"  # Request accepted, thread created
    DECLINED = "declined"  # Request declined


class MessageRequest:
    """
    MessageRequest Entity

    Represents a message request from a stranger (non-friend).
    When accepted, a MessageThread is created.
    Ensures FR-011: Message Requests for strangers.
    """

    def __init__(
        self,
        id: str,
        sender_id: str,
        recipient_id: str,
        initial_message: str,
        post_id: Optional[str],
        status: RequestStatus,
        created_at: datetime,
        updated_at: Optional[datetime] = None,
        thread_id: Optional[str] = None,
    ):
        if not initial_message or len(initial_message.strip()) == 0:
            raise ValueError("Initial message cannot be empty")

        if len(initial_message) > 5000:
            raise ValueError(
                "Initial message exceeds maximum length of 5000 characters"
            )

        if sender_id == recipient_id:
            raise ValueError("Cannot send message request to yourself")

        self.id = id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.initial_message = initial_message
        self.post_id = post_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at or created_at
        self.thread_id = thread_id

    def accept(self, thread_id: str) -> None:
        """Accept the message request and link to thread"""
        if self.status != RequestStatus.PENDING:
            raise ValueError(
                f"Cannot accept request with status {self.status}"
            )
        self.status = RequestStatus.ACCEPTED
        self.thread_id = thread_id
        self.updated_at = datetime.utcnow()

    def decline(self) -> None:
        """Decline the message request"""
        if self.status != RequestStatus.PENDING:
            raise ValueError(
                f"Cannot decline request with status {self.status}"
            )
        self.status = RequestStatus.DECLINED
        self.updated_at = datetime.utcnow()

    def is_pending(self) -> bool:
        """Check if request is pending"""
        return self.status == RequestStatus.PENDING

    def is_accepted(self) -> bool:
        """Check if request is accepted"""
        return self.status == RequestStatus.ACCEPTED

    def is_declined(self) -> bool:
        """Check if request is declined"""
        return self.status == RequestStatus.DECLINED

    def __repr__(self) -> str:
        return (
            f"MessageRequest(id={self.id}, sender_id={self.sender_id}, "
            f"recipient_id={self.recipient_id}, status={self.status})"
        )
