"""
Unit tests for SearchQuotaService

Tests the search quota service for daily search limits.
"""

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.modules.social.infrastructure.services.search_quota_service import (
    SearchQuotaModel,
    SearchQuotaService,
)


DATETIME_PATCH_PATH = (
    "app.modules.social.infrastructure.services.search_quota_service.datetime"
)


class TestSearchQuotaService:
    """Test SearchQuotaService"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance"""
        return SearchQuotaService(session=mock_session)

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_date(self):
        """Create sample date"""
        return date(2024, 1, 24)

    def test_init(self, mock_session):
        """Test service initialization"""
        # Act
        service = SearchQuotaService(session=mock_session)

        # Assert
        assert service.session == mock_session

    def test_get_today_utc(self, service):
        """Test getting today's date in UTC"""
        # Arrange
        expected_date = date(2024, 1, 24)

        # Act
        with patch(DATETIME_PATCH_PATH) as mock_datetime:
            mock_now = MagicMock()
            mock_now.date.return_value = expected_date
            mock_datetime.now.return_value = mock_now

            result = service._get_today_utc()

        # Assert
        assert result == expected_date
        mock_datetime.now.assert_called_once_with(timezone.utc)

    @pytest.mark.asyncio
    async def test_get_today_count_with_existing_record(
        self, service, mock_session, sample_user_id, sample_date
    ):
        """Test getting count when record exists"""
        # Arrange
        expected_count = 3

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(service, "_get_today_utc", return_value=sample_date):
            # Act
            result = await service.get_today_count(sample_user_id)

        # Assert
        assert result == expected_count
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_today_count_with_no_record(
        self, service, mock_session, sample_user_id, sample_date
    ):
        """Test getting count when no record exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(service, "_get_today_utc", return_value=sample_date):
            # Act
            result = await service.get_today_count(sample_user_id)

        # Assert
        assert result == 0
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_increment_count_with_existing_record(
        self, service, mock_session, sample_user_id, sample_date
    ):
        """Test incrementing count when record exists"""
        # Arrange
        existing_quota = SearchQuotaModel(
            user_id=sample_user_id, date=sample_date, count=2
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_quota
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(service, "_get_today_utc", return_value=sample_date):
            # Act
            result = await service.increment_count(sample_user_id)

        # Assert
        assert result == 3
        assert existing_quota.count == 3
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_increment_count_with_no_record(
        self, service, mock_session, sample_user_id, sample_date
    ):
        """Test incrementing count when no record exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(service, "_get_today_utc", return_value=sample_date):
            # Act
            result = await service.increment_count(sample_user_id)

        # Assert
        assert result == 1
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

        # Check that a new quota was added
        added_quota = mock_session.add.call_args[0][0]
        assert isinstance(added_quota, SearchQuotaModel)
        assert added_quota.user_id == sample_user_id
        assert added_quota.date == sample_date
        assert added_quota.count == 1

    @pytest.mark.asyncio
    async def test_check_quota_available_for_premium_user(
        self, service, sample_user_id
    ):
        """Test checking quota for premium user (unlimited)"""
        # Act
        available, count = await service.check_quota_available(
            user_id=sample_user_id, daily_limit=5, is_premium=True
        )

        # Assert
        assert available is True
        assert count == 0

    @pytest.mark.asyncio
    async def test_check_quota_available_for_free_user_under_limit(
        self, service, mock_session, sample_user_id, sample_date
    ):
        """Test checking quota for free user under limit"""
        # Arrange
        current_count = 3
        daily_limit = 5

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = current_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(service, "_get_today_utc", return_value=sample_date):
            # Act
            available, count = await service.check_quota_available(
                user_id=sample_user_id, daily_limit=daily_limit, is_premium=False
            )

        # Assert
        assert available is True
        assert count == current_count

    @pytest.mark.asyncio
    async def test_check_quota_available_for_free_user_at_limit(
        self, service, mock_session, sample_user_id, sample_date
    ):
        """Test checking quota for free user at limit"""
        # Arrange
        current_count = 5
        daily_limit = 5

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = current_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(service, "_get_today_utc", return_value=sample_date):
            # Act
            available, count = await service.check_quota_available(
                user_id=sample_user_id, daily_limit=daily_limit, is_premium=False
            )

        # Assert
        assert available is False
        assert count == current_count

    @pytest.mark.asyncio
    async def test_check_quota_available_for_free_user_over_limit(
        self, service, mock_session, sample_user_id, sample_date
    ):
        """Test checking quota for free user over limit"""
        # Arrange
        current_count = 7
        daily_limit = 5

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = current_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(service, "_get_today_utc", return_value=sample_date):
            # Act
            available, count = await service.check_quota_available(
                user_id=sample_user_id, daily_limit=daily_limit, is_premium=False
            )

        # Assert
        assert available is False
        assert count == current_count

    @pytest.mark.asyncio
    async def test_check_quota_available_for_free_user_no_record(
        self, service, mock_session, sample_user_id, sample_date
    ):
        """Test checking quota for free user with no existing record"""
        # Arrange
        daily_limit = 5

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(service, "_get_today_utc", return_value=sample_date):
            # Act
            available, count = await service.check_quota_available(
                user_id=sample_user_id, daily_limit=daily_limit, is_premium=False
            )

        # Assert
        assert available is True
        assert count == 0


class TestSearchQuotaModel:
    """Test SearchQuotaModel ORM"""

    def test_model_attributes(self):
        """Test model has correct attributes"""
        # Arrange
        user_id = uuid4()
        test_date = date(2024, 1, 24)

        # Act
        model = SearchQuotaModel(user_id=user_id, date=test_date, count=5)

        # Assert
        assert model.user_id == user_id
        assert model.date == test_date
        assert model.count == 5

    def test_model_table_name(self):
        """Test model has correct table name"""
        assert SearchQuotaModel.__tablename__ == "search_quotas"

    def test_model_default_count(self):
        """Test model default count is 0"""
        # Arrange
        user_id = uuid4()
        test_date = date(2024, 1, 24)

        # Act
        # Note: Cannot directly test default on uninitialized model without DB
        # but we can verify the column has the default defined
        column = SearchQuotaModel.__table__.columns["count"]

        # Assert
        assert column.default is not None
        assert column.default.arg == 0
