"""
Comment Entity - Represents a comment on a post

Domain Entity following DDD principles - framework independent
"""

from datetime import datetime, timezone
from typing import Optional


class Comment:
    """
    Comment Entity

    Represents a comment made by a user on a post.
    Comments are displayed in descending order (latest first).
    """

    def __init__(
        self,
        id: str,
        post_id: str,
        user_id: str,
        content: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or self.created_at

        # Validate content
        if not self.content or not self.content.strip():
            raise ValueError("Comment content cannot be empty")
        
        if len(self.content) > 1000:
            raise ValueError("Comment content cannot exceed 1000 characters")
