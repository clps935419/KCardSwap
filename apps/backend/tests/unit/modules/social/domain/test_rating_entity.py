"""
Unit tests for Rating Entity (T126G)
Tests updated for FR-SOCIAL-003A requirements
"""
import pytest
from datetime import datetime
from uuid import uuid4

from app.modules.social.domain.entities.rating import Rating


class TestRatingCreation:
    """Test rating entity creation and validation"""

    def test_rating_creation_with_trade_id(self):
        """Test rating creation with trade_id (trade-based rating)"""
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        trade_id = str(uuid4())
        created_at = datetime.utcnow()

        rating = Rating(
            id=str(uuid4()),
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=5,
            comment="Great trader!",
            created_at=created_at,
            trade_id=trade_id,
        )

        assert rating.rater_id == rater_id
        assert rating.rated_user_id == rated_user_id
        assert rating.trade_id == trade_id
        assert rating.score == 5
        assert rating.comment == "Great trader!"
        assert rating.created_at == created_at

    def test_rating_creation_without_trade_id(self):
        """Test rating creation without trade_id (friendship-based rating per FR-SOCIAL-003A)"""
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        created_at = datetime.utcnow()

        rating = Rating(
            id=str(uuid4()),
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=4,
            comment="Good friend!",
            created_at=created_at,
            trade_id=None,
        )

        assert rating.rater_id == rater_id
        assert rating.rated_user_id == rated_user_id
        assert rating.trade_id is None
        assert rating.score == 4
        assert rating.comment == "Good friend!"

    def test_rating_creation_minimal_fields(self):
        """Test rating creation with minimal required fields (no comment, no trade_id)"""
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        rating = Rating(
            id=str(uuid4()),
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=3,
            comment=None,
            created_at=datetime.utcnow(),
            trade_id=None,
        )

        assert rating.rater_id == rater_id
        assert rating.rated_user_id == rated_user_id
        assert rating.score == 3
        assert rating.comment is None
        assert rating.trade_id is None


class TestRatingValidation:
    """Test rating validation rules"""

    def test_rating_score_must_be_between_1_and_5(self):
        """Test that rating score must be 1-5"""
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Valid scores
        for score in [1, 2, 3, 4, 5]:
            rating = Rating(
                id=str(uuid4()),
                rater_id=rater_id,
                rated_user_id=rated_user_id,
                score=score,
                comment=None,
                created_at=datetime.utcnow(),
            )
            assert rating.score == score

    def test_rating_score_below_1_raises_error(self):
        """Test that score below 1 raises ValueError"""
        with pytest.raises(ValueError, match="Rating score must be between 1 and 5"):
            Rating(
                id=str(uuid4()),
                rater_id=str(uuid4()),
                rated_user_id=str(uuid4()),
                score=0,
                comment=None,
                created_at=datetime.utcnow(),
            )

    def test_rating_score_above_5_raises_error(self):
        """Test that score above 5 raises ValueError"""
        with pytest.raises(ValueError, match="Rating score must be between 1 and 5"):
            Rating(
                id=str(uuid4()),
                rater_id=str(uuid4()),
                rated_user_id=str(uuid4()),
                score=6,
                comment=None,
                created_at=datetime.utcnow(),
            )

    def test_user_cannot_rate_themselves(self):
        """Test that user cannot rate themselves"""
        user_id = str(uuid4())

        with pytest.raises(ValueError, match="User cannot rate themselves"):
            Rating(
                id=str(uuid4()),
                rater_id=user_id,
                rated_user_id=user_id,  # Same as rater_id
                score=5,
                comment=None,
                created_at=datetime.utcnow(),
            )

    def test_comment_cannot_exceed_1000_characters(self):
        """Test that comment length is limited to 1000 characters"""
        long_comment = "x" * 1001

        with pytest.raises(ValueError, match="Rating comment exceeds maximum length"):
            Rating(
                id=str(uuid4()),
                rater_id=str(uuid4()),
                rated_user_id=str(uuid4()),
                score=5,
                comment=long_comment,
                created_at=datetime.utcnow(),
            )

    def test_comment_exactly_1000_characters_is_valid(self):
        """Test that comment with exactly 1000 characters is valid"""
        comment = "x" * 1000

        rating = Rating(
            id=str(uuid4()),
            rater_id=str(uuid4()),
            rated_user_id=str(uuid4()),
            score=5,
            comment=comment,
            created_at=datetime.utcnow(),
        )

        assert len(rating.comment) == 1000


class TestRatingHelperMethods:
    """Test rating helper methods"""

    def test_is_positive_returns_true_for_4_and_5_stars(self):
        """Test is_positive() returns True for 4-5 stars"""
        for score in [4, 5]:
            rating = Rating(
                id=str(uuid4()),
                rater_id=str(uuid4()),
                rated_user_id=str(uuid4()),
                score=score,
                comment=None,
                created_at=datetime.utcnow(),
            )
            assert rating.is_positive() is True

    def test_is_positive_returns_false_for_1_2_3_stars(self):
        """Test is_positive() returns False for 1-3 stars"""
        for score in [1, 2, 3]:
            rating = Rating(
                id=str(uuid4()),
                rater_id=str(uuid4()),
                rated_user_id=str(uuid4()),
                score=score,
                comment=None,
                created_at=datetime.utcnow(),
            )
            assert rating.is_positive() is False

    def test_is_negative_returns_true_for_1_and_2_stars(self):
        """Test is_negative() returns True for 1-2 stars"""
        for score in [1, 2]:
            rating = Rating(
                id=str(uuid4()),
                rater_id=str(uuid4()),
                rated_user_id=str(uuid4()),
                score=score,
                comment=None,
                created_at=datetime.utcnow(),
            )
            assert rating.is_negative() is True

    def test_is_negative_returns_false_for_3_4_5_stars(self):
        """Test is_negative() returns False for 3-5 stars"""
        for score in [3, 4, 5]:
            rating = Rating(
                id=str(uuid4()),
                rater_id=str(uuid4()),
                rated_user_id=str(uuid4()),
                score=score,
                comment=None,
                created_at=datetime.utcnow(),
            )
            assert rating.is_negative() is False
