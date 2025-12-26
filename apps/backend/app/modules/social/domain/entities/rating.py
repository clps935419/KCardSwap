"""
Rating Entity - Represents a user rating after a trade

Domain Entity following DDD principles - framework independent
"""
from datetime import datetime
from typing import Optional


class Rating:
    """
    Rating Entity

    Represents a rating given by one user to another.
    Can be linked to a specific trade or given based on friendship.
    Includes a score (1-5 stars) and optional comment.

    Business Rules (FR-SOCIAL-003A):
    - Score must be 1-5
    - Cannot rate yourself
    - Must be friends OR provide valid trade_id
    - Cannot rate if blocked
    """

    def __init__(
        self,
        id: str,
        rater_id: str,
        rated_user_id: str,
        score: int,
        comment: Optional[str],
        created_at: datetime,
        trade_id: Optional[str] = None,
    ):
        if score < 1 or score > 5:
            raise ValueError("Rating score must be between 1 and 5")

        if rater_id == rated_user_id:
            raise ValueError("User cannot rate themselves")

        if comment and len(comment) > 1000:
            raise ValueError("Rating comment exceeds maximum length of 1000 characters")

        self.id = id
        self.rater_id = rater_id
        self.rated_user_id = rated_user_id
        self.trade_id = trade_id
        self.score = score
        self.comment = comment
        self.created_at = created_at

    def is_positive(self) -> bool:
        """Check if rating is positive (4-5 stars)"""
        return self.score >= 4

    def is_negative(self) -> bool:
        """Check if rating is negative (1-2 stars)"""
        return self.score <= 2

    def __repr__(self) -> str:
        return (
            f"Rating(id={self.id}, rater_id={self.rater_id}, "
            f"rated_user_id={self.rated_user_id}, score={self.score})"
        )
