"""Trade Entity - represents a card exchange transaction between two users."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Trade:
    """
    Trade entity representing a card exchange transaction.
    
    State machine:
    - draft: Initial state when creating a trade (optional, can skip to proposed)
    - proposed: Trade has been proposed to the responder
    - accepted: Responder has accepted the trade
    - completed: Both parties have confirmed completion
    - rejected: Responder has rejected the trade
    - canceled: Trade has been canceled (by user or timeout)
    
    Attributes:
        id: Unique identifier
        initiator_id: User who initiated the trade
        responder_id: User who responds to the trade
        status: Current trade status
        accepted_at: Timestamp when trade was accepted
        initiator_confirmed_at: Timestamp when initiator confirmed completion
        responder_confirmed_at: Timestamp when responder confirmed completion
        completed_at: Timestamp when both parties confirmed (status->completed)
        canceled_at: Timestamp when trade was canceled
        created_at: Timestamp when trade was created
        updated_at: Timestamp when trade was last updated
    """
    
    id: UUID
    initiator_id: UUID
    responder_id: UUID
    status: str
    accepted_at: Optional[datetime] = None
    initiator_confirmed_at: Optional[datetime] = None
    responder_confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Valid status values
    STATUS_DRAFT = "draft"
    STATUS_PROPOSED = "proposed"
    STATUS_ACCEPTED = "accepted"
    STATUS_COMPLETED = "completed"
    STATUS_REJECTED = "rejected"
    STATUS_CANCELED = "canceled"
    
    VALID_STATUSES = {
        STATUS_DRAFT,
        STATUS_PROPOSED,
        STATUS_ACCEPTED,
        STATUS_COMPLETED,
        STATUS_REJECTED,
        STATUS_CANCELED,
    }
    
    def __post_init__(self):
        """Validate entity invariants."""
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid trade status: {self.status}")
        
        if self.initiator_id == self.responder_id:
            raise ValueError("Initiator and responder must be different users")
        
        # Validate completed state
        if self.status == self.STATUS_COMPLETED:
            if not self.completed_at:
                raise ValueError("Completed trade must have completed_at timestamp")
            if not self.initiator_confirmed_at or not self.responder_confirmed_at:
                raise ValueError(
                    "Completed trade must have both confirmations"
                )
    
    def can_accept(self) -> bool:
        """Check if trade can be accepted."""
        return self.status == self.STATUS_PROPOSED
    
    def can_reject(self) -> bool:
        """Check if trade can be rejected."""
        return self.status in (self.STATUS_PROPOSED, self.STATUS_DRAFT)
    
    def can_cancel(self) -> bool:
        """Check if trade can be canceled."""
        return self.status in (
            self.STATUS_DRAFT,
            self.STATUS_PROPOSED,
            self.STATUS_ACCEPTED,
        )
    
    def can_confirm(self) -> bool:
        """Check if trade can be confirmed by a party."""
        return self.status == self.STATUS_ACCEPTED
    
    def is_completed(self) -> bool:
        """Check if both parties have confirmed completion."""
        return (
            self.initiator_confirmed_at is not None
            and self.responder_confirmed_at is not None
        )
    
    def is_active(self) -> bool:
        """Check if trade is in an active state (not terminal)."""
        return self.status in (
            self.STATUS_DRAFT,
            self.STATUS_PROPOSED,
            self.STATUS_ACCEPTED,
        )
    
    def is_terminal(self) -> bool:
        """Check if trade is in a terminal state."""
        return self.status in (
            self.STATUS_COMPLETED,
            self.STATUS_REJECTED,
            self.STATUS_CANCELED,
        )
    
    def has_user(self, user_id: UUID) -> bool:
        """Check if user is a participant in this trade."""
        return user_id in (self.initiator_id, self.responder_id)
    
    def is_initiator(self, user_id: UUID) -> bool:
        """Check if user is the initiator."""
        return user_id == self.initiator_id
    
    def is_responder(self, user_id: UUID) -> bool:
        """Check if user is the responder."""
        return user_id == self.responder_id
