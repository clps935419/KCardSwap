"""
PostLike domain entity
Represents a user's like on a post (FR-008, FR-009)
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class PostLike:
    """
    PostLike entity - represents a user's like on a post

    FR-009: Each user can like a post at most once (enforced by unique constraint)
    """

    id: str
    post_id: str
    user_id: str
    created_at: datetime

    @staticmethod
    def create(
        post_id: str,
        user_id: str,
    ) -> "PostLike":
        """Factory method to create a new like"""
        return PostLike(
            id=str(uuid4()),
            post_id=post_id,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
        )
