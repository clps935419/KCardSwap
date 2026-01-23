"""
MessageThread Entity - Represents a unique conversation thread between two users

Domain Entity following DDD principles - framework independent
"""

from datetime import datetime
from typing import Optional


class MessageThread:
    """
    MessageThread Entity

    Represents a unique conversation thread between two users.
    Ensures FR-014: One unique thread per user pair.
    
    Implementation note: user_a_id and user_b_id are stored in normalized order
    (smaller UUID first) to ensure uniqueness constraint at DB level.
    """

    def __init__(
        self,
        id: str,
        user_a_id: str,
        user_b_id: str,
        created_at: datetime,
        updated_at: datetime,
        last_message_at: Optional[datetime] = None,
    ):
        if user_a_id == user_b_id:
            raise ValueError("Cannot create thread with same user")

        # Normalize user order for uniqueness (smaller UUID first)
        if user_a_id > user_b_id:
            user_a_id, user_b_id = user_b_id, user_a_id

        self.id = id
        self.user_a_id = user_a_id
        self.user_b_id = user_b_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_message_at = last_message_at

    def update_last_message_time(self, message_time: datetime) -> None:
        """Update the last message timestamp"""
        self.last_message_at = message_time
        self.updated_at = datetime.utcnow()

    def has_user(self, user_id: str) -> bool:
        """Check if user is part of this thread"""
        return user_id in (self.user_a_id, self.user_b_id)

    def get_other_user_id(self, user_id: str) -> str:
        """Get the other user in the thread"""
        if not self.has_user(user_id):
            raise ValueError("User is not part of this thread")
        return self.user_b_id if user_id == self.user_a_id else self.user_a_id

    def __repr__(self) -> str:
        return (
            f"MessageThread(id={self.id}, user_a_id={self.user_a_id}, "
            f"user_b_id={self.user_b_id})"
        )
