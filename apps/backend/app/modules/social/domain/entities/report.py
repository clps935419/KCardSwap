"""
Report Entity - Represents a user report for violations

Domain Entity following DDD principles - framework independent
"""
from datetime import datetime
from enum import Enum
from typing import Optional


class ReportReason(str, Enum):
    """Report reason enumeration"""

    FRAUD = "fraud"  # Suspected fraud/scam
    FAKE_CARD = "fake_card"  # Fake card image
    HARASSMENT = "harassment"  # Harassment or abusive behavior
    INAPPROPRIATE_CONTENT = "inappropriate_content"  # Inappropriate messages/images
    SPAM = "spam"  # Spam or repeated unwanted messages
    OTHER = "other"  # Other reasons


class Report:
    """
    Report Entity

    Represents a report filed by one user against another for policy violations.
    Supports various violation types and optional detailed explanation.
    """

    def __init__(
        self,
        id: str,
        reporter_id: str,
        reported_user_id: str,
        reason: ReportReason,
        detail: Optional[str],
        created_at: datetime,
        resolved: bool = False,
        resolved_at: Optional[datetime] = None,
    ):
        if reporter_id == reported_user_id:
            raise ValueError("User cannot report themselves")

        if detail and len(detail) > 2000:
            raise ValueError("Report detail exceeds maximum length of 2000 characters")

        self.id = id
        self.reporter_id = reporter_id
        self.reported_user_id = reported_user_id
        self.reason = reason
        self.detail = detail
        self.created_at = created_at
        self.resolved = resolved
        self.resolved_at = resolved_at

    def mark_resolved(self) -> None:
        """Mark report as resolved"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()

    def is_serious_violation(self) -> bool:
        """Check if report is for a serious violation"""
        return self.reason in (
            ReportReason.FRAUD,
            ReportReason.FAKE_CARD,
            ReportReason.HARASSMENT,
        )

    def __repr__(self) -> str:
        return (
            f"Report(id={self.id}, reporter_id={self.reporter_id}, "
            f"reported_user_id={self.reported_user_id}, reason={self.reason}, "
            f"resolved={self.resolved})"
        )
