"""
Post Entity - Represents a city board post for card exchange

Domain Entity following DDD principles - framework independent
"""
from datetime import datetime
from enum import Enum
from typing import Optional


class PostStatus(str, Enum):
    """Post status enumeration"""

    OPEN = "open"
    CLOSED = "closed"
    EXPIRED = "expired"
    DELETED = "deleted"


class Post:
    """
    Post Entity

    Represents a city board post where users can initiate card exchanges.
    Posts are associated with a specific city and can be filtered by idol/idol_group.
    """

    def __init__(
        self,
        id: str,
        owner_id: str,
        city_code: str,
        title: str,
        content: str,
        status: PostStatus,
        expires_at: datetime,
        idol: Optional[str] = None,
        idol_group: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.owner_id = owner_id
        self.city_code = city_code
        self.title = title
        self.content = content
        self.idol = idol
        self.idol_group = idol_group
        self.status = status
        self.expires_at = expires_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at

    def close(self) -> None:
        """Close the post manually"""
        if self.status != PostStatus.OPEN:
            raise ValueError(f"Cannot close post with status {self.status}")
        self.status = PostStatus.CLOSED
        self.updated_at = datetime.utcnow()

    def mark_expired(self) -> None:
        """Mark the post as expired"""
        if self.status != PostStatus.OPEN:
            raise ValueError(f"Cannot expire post with status {self.status}")
        self.status = PostStatus.EXPIRED
        self.updated_at = datetime.utcnow()

    def delete(self) -> None:
        """Delete the post (soft delete)"""
        self.status = PostStatus.DELETED
        self.updated_at = datetime.utcnow()

    def is_open(self) -> bool:
        """Check if post is open"""
        return self.status == PostStatus.OPEN

    def is_expired(self) -> bool:
        """Check if post has expired"""
        return datetime.utcnow() > self.expires_at

    def can_accept_interests(self) -> bool:
        """Check if post can accept new interests"""
        return self.status == PostStatus.OPEN and not self.is_expired()
