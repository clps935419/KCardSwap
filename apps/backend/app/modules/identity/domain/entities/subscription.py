"""
Subscription Entity - Represents user subscription status and plan
"""

from datetime import datetime
from typing import Optional
from uuid import UUID


class Subscription:
    """
    Subscription entity representing a user's subscription plan and status.

    Status values:
    - active: Subscription is currently active and valid
    - expired: Subscription has expired
    - inactive: No subscription or canceled before expiry
    - pending: Google Play purchase is pending confirmation
    """

    def __init__(
        self,
        id: Optional[UUID],
        user_id: UUID,
        plan: str,  # "free" or "premium"
        status: str,  # "active", "inactive", "expired", "pending"
        expires_at: Optional[datetime],
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.plan = plan
        self.status = status
        self.expires_at = expires_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status != "active":
            return False
        if self.expires_at is None:
            return False
        return datetime.utcnow() < self.expires_at

    def is_premium(self) -> bool:
        """Check if user has premium plan"""
        return self.plan == "premium" and self.is_active()

    def should_expire(self) -> bool:
        """Check if subscription should be marked as expired"""
        if self.status == "active" and self.expires_at is not None:
            return datetime.utcnow() >= self.expires_at
        return False

    def mark_as_expired(self) -> None:
        """Mark subscription as expired"""
        self.status = "expired"
        self.updated_at = datetime.utcnow()

    def activate(self, expires_at: datetime) -> None:
        """Activate premium subscription"""
        self.plan = "premium"
        self.status = "active"
        self.expires_at = expires_at
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate subscription (return to free)"""
        self.plan = "free"
        self.status = "inactive"
        self.expires_at = None
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<Subscription(id={self.id}, user_id={self.user_id}, "
            f"plan={self.plan}, status={self.status}, "
            f"expires_at={self.expires_at})>"
        )
