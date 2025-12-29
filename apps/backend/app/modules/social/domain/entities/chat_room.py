"""
ChatRoom Entity - Represents a one-on-one chat room between two users

Domain Entity following DDD principles - framework independent
"""

from datetime import datetime
from typing import List


class ChatRoom:
    """
    ChatRoom Entity

    Represents a one-on-one chat room between two users.
    Each pair of users has exactly one chat room.
    """

    def __init__(self, id: str, participant_ids: List[str], created_at: datetime):
        if len(participant_ids) != 2:
            raise ValueError("ChatRoom must have exactly 2 participants")

        self.id = id
        # Store sorted to ensure consistency
        self.participant_ids = sorted(participant_ids)
        self.created_at = created_at

    def has_participant(self, user_id: str) -> bool:
        """Check if user is a participant in this chat room"""
        return user_id in self.participant_ids

    def get_other_participant(self, user_id: str) -> str:
        """Get the other participant's ID given one user's ID"""
        if not self.has_participant(user_id):
            raise ValueError(f"User {user_id} is not a participant in this chat room")
        return next(pid for pid in self.participant_ids if pid != user_id)

    def __repr__(self) -> str:
        return f"ChatRoom(id={self.id}, participants={self.participant_ids})"
