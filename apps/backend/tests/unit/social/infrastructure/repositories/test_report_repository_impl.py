"""
Unit tests for ReportRepositoryImpl

Tests the report repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.report import Report, ReportReason
from app.modules.social.infrastructure.database.models.report_model import ReportModel
from app.modules.social.infrastructure.repositories.report_repository_impl import (
    ReportRepositoryImpl,
)


class TestReportRepositoryImpl:
    """Test ReportRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return ReportRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_report(self):
        """Create sample Report entity"""
        return Report(
            id=str(uuid4()),
            reporter_id=str(uuid4()),
            reported_user_id=str(uuid4()),
            reason=ReportReason.HARASSMENT,
            detail="User was rude during trade",
            resolved=False,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_report_model(self, sample_report):
        """Create sample ReportModel"""
        return ReportModel(
            id=UUID(sample_report.id),
            reporter_id=UUID(sample_report.reporter_id),
            reported_user_id=UUID(sample_report.reported_user_id),
            reason=sample_report.reason.value,
            detail=sample_report.detail,
            resolved=sample_report.resolved,
            created_at=sample_report.created_at,
        )

    @pytest.mark.asyncio
    async def test_create_report(self, repository, mock_session, sample_report):
        """Test creating a report"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_report)

        # Assert
        assert result is not None
        assert result.id == sample_report.id
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_report_model):
        """Test getting report by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_report_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(sample_report_model.id))

        # Assert
        assert result is not None
        assert result.id == str(sample_report_model.id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting report by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_reports_by_reported_user_id(self, repository, mock_session):
        """Test getting reports by reported user ID"""
        # Arrange
        reported_user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_reports_by_reported_user_id(reported_user_id)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reports_by_reported_user_id_with_filter(
        self, repository, mock_session
    ):
        """Test getting reports filtered by resolution status"""
        # Arrange
        reported_user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_reports_by_reported_user_id(
            reported_user_id, resolved=False
        )

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reports_by_reporter_id(self, repository, mock_session):
        """Test getting reports by reporter ID"""
        # Arrange
        reporter_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_reports_by_reporter_id(reporter_id)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_reporter(self, repository, mock_session):
        """Test finding reports by reporter (alias method)"""
        # Arrange
        reporter_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_reporter(reporter_id)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_unresolved_reports(self, repository, mock_session):
        """Test getting unresolved reports"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_unresolved_reports(limit=50)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_report(
        self, repository, mock_session, sample_report, sample_report_model
    ):
        """Test updating a report"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_report_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Modify the report
        sample_report.resolved = True

        # Act
        result = await repository.update(sample_report)

        # Assert
        assert result is not None
        assert result.id == sample_report.id

    @pytest.mark.asyncio
    async def test_get_report_count_by_user(self, repository, mock_session):
        """Test getting report count for a user"""
        # Arrange
        reported_user_id = str(uuid4())
        expected_count = 3

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_report_count_by_user(reported_user_id)

        # Assert
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_get_report_count_by_user_with_reason(self, repository, mock_session):
        """Test getting report count filtered by reason"""
        # Arrange
        reported_user_id = str(uuid4())
        expected_count = 1

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_report_count_by_user(
            reported_user_id, reason=ReportReason.HARASSMENT
        )

        # Assert
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_delete_report(self, repository, mock_session, sample_report_model):
        """Test deleting a report"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_report_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_report_model.id))

        # Assert
        mock_session.delete.assert_called_once()
