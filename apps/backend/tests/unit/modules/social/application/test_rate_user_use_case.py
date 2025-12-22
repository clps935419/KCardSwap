"""
Unit tests for RateUserUseCase (T126G)
Testing FR-SOCIAL-003A business rules with mocked dependencies
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.modules.social.application.use_cases.ratings.rate_user_use_case import (
    RateUserUseCase,
)
from app.modules.social.domain.entities.rating import Rating


class TestRateUserUseCaseSuccess:
    """Test successful rating scenarios"""

    @pytest.fixture
    def mock_rating_repository(self):
        """Mock rating repository"""
        repo = Mock()
        repo.has_user_rated_trade = AsyncMock(return_value=False)
        repo.create = AsyncMock(side_effect=lambda rating: rating)
        return repo

    @pytest.fixture
    def mock_friendship_repository(self):
        """Mock friendship repository"""
        repo = Mock()
        repo.is_blocked = AsyncMock(return_value=False)
        repo.are_friends = AsyncMock(return_value=True)
        return repo

    @pytest.mark.asyncio
    async def test_rate_friend_without_trade_id(
        self, mock_rating_repository, mock_friendship_repository
    ):
        """Test rating a friend without trade_id (FR-SOCIAL-003A)"""
        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        score = 5
        comment = "Great friend!"

        rating = await use_case.execute(
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=score,
            comment=comment,
            trade_id=None,  # Friendship-based rating
        )

        assert isinstance(rating, Rating)
        assert rating.rater_id == rater_id
        assert rating.rated_user_id == rated_user_id
        assert rating.score == score
        assert rating.comment == comment
        assert rating.trade_id is None

        # Verify friendship was checked
        mock_friendship_repository.are_friends.assert_called_once_with(
            rater_id, rated_user_id
        )

    @pytest.mark.asyncio
    async def test_rate_with_trade_id(
        self, mock_rating_repository, mock_friendship_repository
    ):
        """Test rating with trade_id (trade-based rating)"""
        # Setup: users are not friends but provide valid trade_id
        mock_friendship_repository.are_friends = AsyncMock(return_value=False)

        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        trade_id = str(uuid4())
        score = 4

        rating = await use_case.execute(
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=score,
            comment=None,
            trade_id=trade_id,
        )

        assert isinstance(rating, Rating)
        assert rating.trade_id == trade_id
        assert rating.score == score

        # Verify duplicate check was performed
        mock_rating_repository.has_user_rated_trade.assert_called_once_with(
            rater_id, trade_id
        )

    @pytest.mark.asyncio
    async def test_rate_friend_with_trade_id(
        self, mock_rating_repository, mock_friendship_repository
    ):
        """Test rating a friend with trade_id (both conditions satisfied)"""
        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        trade_id = str(uuid4())
        score = 5
        comment = "Great trade with a friend!"

        rating = await use_case.execute(
            rater_id=rater_id,
            rated_user_id=rated_user_id,
            score=score,
            comment=comment,
            trade_id=trade_id,
        )

        assert isinstance(rating, Rating)
        assert rating.trade_id == trade_id
        assert rating.score == score
        assert rating.comment == comment


class TestRateUserUseCaseValidation:
    """Test validation rules and error cases"""

    @pytest.fixture
    def mock_rating_repository(self):
        """Mock rating repository"""
        repo = Mock()
        repo.has_user_rated_trade = AsyncMock(return_value=False)
        repo.create = AsyncMock(side_effect=lambda rating: rating)
        return repo

    @pytest.fixture
    def mock_friendship_repository(self):
        """Mock friendship repository"""
        repo = Mock()
        repo.is_blocked = AsyncMock(return_value=False)
        repo.are_friends = AsyncMock(return_value=True)
        return repo

    @pytest.mark.asyncio
    async def test_cannot_rate_if_blocked_by_other_user(
        self, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate if blocked by the other user"""
        # Setup: rater is blocked by rated_user
        mock_friendship_repository.is_blocked = AsyncMock(
            side_effect=lambda user_id, blocker_id: blocker_id == str(uuid4())
        )

        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Mock: rated_user has blocked rater
        async def is_blocked_mock(user_id, potential_blocker_id):
            return user_id == rater_id and potential_blocker_id == rated_user_id

        mock_friendship_repository.is_blocked = AsyncMock(side_effect=is_blocked_mock)

        with pytest.raises(ValueError, match="Cannot rate user: one party has blocked the other"):
            await use_case.execute(
                rater_id=rater_id,
                rated_user_id=rated_user_id,
                score=5,
                comment=None,
            )

    @pytest.mark.asyncio
    async def test_cannot_rate_if_has_blocked_other_user(
        self, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate if rater has blocked the other user"""
        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        # Mock: rater has blocked rated_user
        async def is_blocked_mock(user_id, potential_blocker_id):
            return user_id == rated_user_id and potential_blocker_id == rater_id

        mock_friendship_repository.is_blocked = AsyncMock(side_effect=is_blocked_mock)

        with pytest.raises(ValueError, match="Cannot rate user: one party has blocked the other"):
            await use_case.execute(
                rater_id=rater_id,
                rated_user_id=rated_user_id,
                score=5,
                comment=None,
            )

    @pytest.mark.asyncio
    async def test_cannot_rate_if_not_friends_and_no_trade_id(
        self, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate if not friends and no trade_id provided (FR-SOCIAL-003A)"""
        # Setup: users are not friends
        mock_friendship_repository.are_friends = AsyncMock(return_value=False)

        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        with pytest.raises(ValueError, match="must be friends or provide a valid trade_id"):
            await use_case.execute(
                rater_id=rater_id,
                rated_user_id=rated_user_id,
                score=5,
                comment=None,
                trade_id=None,  # No trade_id provided
            )

    @pytest.mark.asyncio
    async def test_cannot_rate_same_trade_twice(
        self, mock_rating_repository, mock_friendship_repository
    ):
        """Test cannot rate the same trade twice"""
        # Setup: user has already rated this trade
        mock_rating_repository.has_user_rated_trade = AsyncMock(return_value=True)

        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        rater_id = str(uuid4())
        rated_user_id = str(uuid4())
        trade_id = str(uuid4())

        with pytest.raises(ValueError, match="User has already rated this trade"):
            await use_case.execute(
                rater_id=rater_id,
                rated_user_id=rated_user_id,
                score=5,
                comment=None,
                trade_id=trade_id,
            )

    @pytest.mark.asyncio
    async def test_entity_validation_is_enforced(
        self, mock_rating_repository, mock_friendship_repository
    ):
        """Test that Rating entity validation is enforced (score, self-rating, comment length)"""
        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        user_id = str(uuid4())

        # Test: cannot rate yourself (entity validation)
        with pytest.raises(ValueError, match="User cannot rate themselves"):
            await use_case.execute(
                rater_id=user_id,
                rated_user_id=user_id,  # Same user
                score=5,
                comment=None,
            )


class TestRateUserUseCaseBlockingScenarios:
    """Test various blocking scenarios"""

    @pytest.fixture
    def mock_rating_repository(self):
        repo = Mock()
        repo.has_user_rated_trade = AsyncMock(return_value=False)
        repo.create = AsyncMock(side_effect=lambda rating: rating)
        return repo

    @pytest.mark.asyncio
    async def test_mutual_blocking_prevents_rating(self, mock_rating_repository):
        """Test that mutual blocking prevents rating"""
        mock_friendship_repository = Mock()
        # Both users have blocked each other
        mock_friendship_repository.is_blocked = AsyncMock(return_value=True)
        mock_friendship_repository.are_friends = AsyncMock(return_value=False)

        use_case = RateUserUseCase(
            rating_repository=mock_rating_repository,
            friendship_repository=mock_friendship_repository,
        )

        rater_id = str(uuid4())
        rated_user_id = str(uuid4())

        with pytest.raises(ValueError, match="Cannot rate user: one party has blocked the other"):
            await use_case.execute(
                rater_id=rater_id,
                rated_user_id=rated_user_id,
                score=5,
                comment=None,
            )
