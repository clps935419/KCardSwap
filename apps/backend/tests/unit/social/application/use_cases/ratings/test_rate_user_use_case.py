"""
Unit tests for RateUserUseCase

Tests the rating use case implementation with mocked repositories.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.ratings.rate_user_use_case import (
    RateUserUseCase,
)


class TestRateUserUseCase:
    """Test RateUserUseCase"""

    @pytest.fixture
    def mock_rating_repository(self):
        """Create mock rating repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_friendship_repository(self):
        """Create mock friendship repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_rating_repository, mock_friendship_repository):
        """Create use case instance"""
        return RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

    @pytest.mark.asyncio
    async def test_rate_user_success_with_friendship(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test successful rating creation based on friendship"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        score = 5
        comment = "Great trader!"

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock are friends
        mock_friendship_repository.are_friends.return_value = True

        # Mock rating creation
        def create_side_effect(rating):
            return rating

        mock_rating_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=score,
            comment=comment,
        )

        # Assert
        assert result is not None
        assert result.rater_id == rater_id
        assert result.rated_user_id == rated_user_id
        assert result.score == score
        assert result.comment == comment
        assert result.trade_id is None

        # Verify repository calls
        mock_friendship_repository.is_blocked.assert_any_call(rated_user_id, rater_id)
        mock_friendship_repository.is_blocked.assert_any_call(rater_id, rated_user_id)
        mock_friendship_repository.are_friends.assert_called_once_with(
            rater_id, rated_user_id
        )
        mock_rating_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_user_success_with_trade_id(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test successful rating creation with trade_id"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        trade_id = str(uuid4())
        score = 4
        comment = "Good trade"

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock not friends (but has trade_id)
        mock_friendship_repository.are_friends.return_value = False
        # Mock user hasn't rated this trade yet
        mock_rating_repository.has_user_rated_trade.return_value = False

        # Mock rating creation
        def create_side_effect(rating):
            return rating

        mock_rating_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=score,
            comment=comment,
            trade_id=trade_id,
        )

        # Assert
        assert result is not None
        assert result.rater_id == rater_id
        assert result.rated_user_id == rated_user_id
        assert result.score == score
        assert result.comment == comment
        assert result.trade_id == trade_id

        # Verify repository calls
        mock_rating_repository.has_user_rated_trade.assert_called_once_with(
            rater_id, trade_id
        )
        mock_rating_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_user_blocked_by_rated_user(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate when blocked by the rated user"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Mock rater is blocked by rated_user
        def is_blocked_side_effect(user_id, blocked_id):
            return user_id == rated_user_id and blocked_id == rater_id

        mock_friendship_repository.is_blocked.side_effect = is_blocked_side_effect

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot rate user: one party has blocked the other"
        ):
            await use_case.execute(
                rater_id=rater_id, rated_user_id=rated_user_id, score=5
            )

        # Verify create was not called
        mock_rating_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_user_has_blocked_rated_user(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate when rater has blocked the rated user"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Mock rater has blocked rated_user
        def is_blocked_side_effect(user_id, blocked_id):
            return user_id == rater_id and blocked_id == rated_user_id

        mock_friendship_repository.is_blocked.side_effect = is_blocked_side_effect

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot rate user: one party has blocked the other"
        ):
            await use_case.execute(
                rater_id=rater_id, rated_user_id=rated_user_id, score=5
            )

        # Verify create was not called
        mock_rating_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_user_not_friends_and_no_trade_id(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate when not friends and no trade_id provided"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock not friends
        mock_friendship_repository.are_friends.return_value = False

        # Act & Assert
        with pytest.raises(
            ValueError,
            match="Cannot rate user: must be friends or provide a valid trade_id",
        ):
            await use_case.execute(
                rater_id=rater_id, rated_user_id=rated_user_id, score=5
            )

        # Verify create was not called
        mock_rating_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_user_duplicate_rating_for_trade(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate same trade twice"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        trade_id = str(uuid4())

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock not friends (but has trade_id)
        mock_friendship_repository.are_friends.return_value = False
        # Mock user has already rated this trade
        mock_rating_repository.has_user_rated_trade.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="User has already rated this trade"):
            await use_case.execute(
                rater_id=rater_id,
                rated_user_id=rated_user_id,
                score=5,
                trade_id=trade_id,
            )

        # Verify create was not called
        mock_rating_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_user_invalid_score_too_low(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test rating validation: score too low"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock are friends
        mock_friendship_repository.are_friends.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Rating score must be between 1 and 5"):
            await use_case.execute(
                rater_id=rater_id, rated_user_id=rated_user_id, score=0
            )

        # Verify create was not called
        mock_rating_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_user_invalid_score_too_high(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test rating validation: score too high"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock are friends
        mock_friendship_repository.are_friends.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Rating score must be between 1 and 5"):
            await use_case.execute(
                rater_id=rater_id, rated_user_id=rated_user_id, score=6
            )

        # Verify create was not called
        mock_rating_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_user_cannot_rate_self(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate yourself"""
        # Arrange
        user_id = str(uuid4())

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock are friends (with yourself - edge case)
        mock_friendship_repository.are_friends.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="User cannot rate themselves"):
            await use_case.execute(rater_id=user_id, rated_user_id=user_id, score=5)

        # Verify create was not called
        mock_rating_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_user_comment_too_long(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test rating validation: comment too long"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        long_comment = "x" * 1001  # Exceeds 1000 char limit

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock are friends
        mock_friendship_repository.are_friends.return_value = True

        # Act & Assert
        with pytest.raises(
            ValueError, match="Rating comment exceeds maximum length of 1000 characters"
        ):
            await use_case.execute(
                rater_id=rater_id,
                rated_user_id=rated_user_id,
                score=5,
                comment=long_comment,
            )

        # Verify create was not called
        mock_rating_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_user_with_valid_comment(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test successful rating with valid comment length"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        valid_comment = "x" * 1000  # Exactly at 1000 char limit

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock are friends
        mock_friendship_repository.are_friends.return_value = True

        # Mock rating creation
        def create_side_effect(rating):
            return rating

        mock_rating_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=5,
            comment=valid_comment,
        )

        # Assert
        assert result is not None
        assert result.comment == valid_comment
        mock_rating_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_user_all_valid_scores(
        self, use_case, mock_rating_repository, mock_friendship_repository
    ):
        """Test all valid score values (1-5)"""
        # Arrange
        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Mock no blocking
        mock_friendship_repository.is_blocked.return_value = False
        # Mock are friends
        mock_friendship_repository.are_friends.return_value = True

        # Mock rating creation
        def create_side_effect(rating):
            return rating

        mock_rating_repository.create.side_effect = create_side_effect

        # Act & Assert - test all valid scores
        for score in [1, 2, 3, 4, 5]:
            result = await use_case.execute(
                rater_id=rater_id, rated_user_id=rated_user_id, score=score
            )
            assert result.score == score

        # Verify create was called 5 times
        assert mock_rating_repository.create.call_count == 5
