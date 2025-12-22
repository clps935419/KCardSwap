"""Trade Status Value Object - encapsulates trade status transition logic."""

from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class TradeStatus:
    """
    Value object representing a trade status with transition rules.
    
    State machine transitions:
    - draft -> proposed: Initiator finalizes and sends the proposal
    - draft -> canceled: Initiator cancels before sending
    - proposed -> accepted: Responder accepts the proposal
    - proposed -> rejected: Responder rejects the proposal
    - proposed -> canceled: Initiator cancels the proposal
    - accepted -> completed: Both parties confirm completion
    - accepted -> canceled: Either party cancels or timeout occurs
    """
    
    value: str
    
    # Status constants
    DRAFT = "draft"
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELED = "canceled"
    
    # Valid statuses
    VALID_STATUSES = {DRAFT, PROPOSED, ACCEPTED, COMPLETED, REJECTED, CANCELED}
    
    # Terminal statuses (cannot transition from these)
    TERMINAL_STATUSES = {COMPLETED, REJECTED, CANCELED}
    
    # Active statuses (trade is in progress)
    ACTIVE_STATUSES = {DRAFT, PROPOSED, ACCEPTED}
    
    def __post_init__(self):
        """Validate status value."""
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid trade status: {self.value}")
    
    def can_transition_to(self, new_status: str) -> bool:
        """
        Check if transition to new status is valid.
        
        Args:
            new_status: Target status to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        if new_status not in self.VALID_STATUSES:
            return False
        
        # Cannot transition from terminal statuses
        if self.is_terminal():
            return False
        
        # Get valid transitions for current status
        valid_transitions = self._get_valid_transitions()
        return new_status in valid_transitions
    
    def _get_valid_transitions(self) -> Set[str]:
        """Get set of valid transitions from current status."""
        transitions = {
            self.DRAFT: {self.PROPOSED, self.CANCELED},
            self.PROPOSED: {self.ACCEPTED, self.REJECTED, self.CANCELED},
            self.ACCEPTED: {self.COMPLETED, self.CANCELED},
            self.COMPLETED: set(),  # Terminal
            self.REJECTED: set(),  # Terminal
            self.CANCELED: set(),  # Terminal
        }
        return transitions.get(self.value, set())
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal status."""
        return self.value in self.TERMINAL_STATUSES
    
    def is_active(self) -> bool:
        """Check if this is an active status."""
        return self.value in self.ACTIVE_STATUSES
    
    def is_draft(self) -> bool:
        """Check if status is draft."""
        return self.value == self.DRAFT
    
    def is_proposed(self) -> bool:
        """Check if status is proposed."""
        return self.value == self.PROPOSED
    
    def is_accepted(self) -> bool:
        """Check if status is accepted."""
        return self.value == self.ACCEPTED
    
    def is_completed(self) -> bool:
        """Check if status is completed."""
        return self.value == self.COMPLETED
    
    def is_rejected(self) -> bool:
        """Check if status is rejected."""
        return self.value == self.REJECTED
    
    def is_canceled(self) -> bool:
        """Check if status is canceled."""
        return self.value == self.CANCELED
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if isinstance(other, TradeStatus):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.value)
