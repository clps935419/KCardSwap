"""
PostInterest Entity - Represents user interest in a city board post

Domain Entity following DDD principles - framework independent
"""
from datetime import datetime
from enum import Enum
from typing import Optional


class PostInterestStatus(str, Enum):
    """Post interest status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PostInterest:
    """
    PostInterest Entity

    Represents a user's expression of interest in a post.
    The post owner can accept or reject the interest.
    """

    def __init__(
        self,
        id: str,
        post_id: str,
        user_id: str,
        status: PostInterestStatus,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.post_id = post_id
        self.user_id = user_id
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at

    def accept(self) -> None:
        """Accept the interest"""
        if self.status != PostInterestStatus.PENDING:
            raise ValueError(f"Cannot accept interest with status {self.status}")
        self.status = PostInterestStatus.ACCEPTED
        self.updated_at = datetime.utcnow()

    def reject(self) -> None:
        """Reject the interest"""
        if self.status != PostInterestStatus.PENDING:
            raise ValueError(f"Cannot reject interest with status {self.status}")
        self.status = PostInterestStatus.REJECTED
        self.updated_at = datetime.utcnow()

    def is_pending(self) -> bool:
        """Check if interest is pending"""
        return self.status == PostInterestStatus.PENDING

    def is_accepted(self) -> bool:
        """Check if interest is accepted"""
        return self.status == PostInterestStatus.ACCEPTED
