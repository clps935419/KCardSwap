"""
Unit tests for Report Router

Tests the report router endpoints:
- POST /reports - Submit a report
- GET /reports - Get my reports
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modules.social.domain.entities.report import ReportReason


class TestReportRouter:
    """Test cases for Report Router endpoints"""

    @pytest.fixture
    def mock_report_repo(self):
        """Mock report repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_report_use_case(self):
        """Mock report user use case"""
        return AsyncMock()

    @pytest.fixture
    def current_user_id(self):
        """Current authenticated user ID"""
        return uuid4()

    @pytest.fixture
    def reported_user_id(self):
        """Reported user ID"""
        return uuid4()

    @pytest.fixture
    def mock_report_entity(self, current_user_id, reported_user_id):
        """Mock report entity"""
        mock_report = AsyncMock()
        mock_report.id = str(uuid4())
        mock_report.reporter_id = str(current_user_id)
        mock_report.reported_user_id = str(reported_user_id)
        mock_report.reason = ReportReason.HARASSMENT
        mock_report.detail = "Test harassment report"
        mock_report.created_at = datetime.utcnow()
        return mock_report

    # Submit Report Tests

    @pytest.mark.asyncio
    async def test_submit_report_success(
        self, mock_report_use_case, mock_report_entity, current_user_id, reported_user_id
    ):
        """Test successfully submitting a report"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import submit_report
        from app.modules.social.presentation.schemas.report_schemas import ReportRequest

        request = ReportRequest(
            reported_user_id=reported_user_id,
            reason=ReportReason.HARASSMENT,
            detail="Test harassment report",
        )
        mock_session = AsyncMock()

        mock_report_use_case.execute.return_value = mock_report_entity

        # Act
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportUserUseCase",
            return_value=mock_report_use_case,
        ):
            result = await submit_report(
                request=request,
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        assert result.data.reported_user_id == reported_user_id
        assert result.data.reason == ReportReason.HARASSMENT
        assert result.data.detail == "Test harassment report"
        assert result.data.status == "pending"
        assert result.error is None
        mock_report_use_case.execute.assert_called_once_with(
            reporter_id=str(current_user_id),
            reported_user_id=str(reported_user_id),
            reason=ReportReason.HARASSMENT,
            detail="Test harassment report",
        )

    @pytest.mark.asyncio
    async def test_submit_report_fraud_reason(
        self, mock_report_use_case, mock_report_entity, current_user_id, reported_user_id
    ):
        """Test submitting a report with fraud reason"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import submit_report
        from app.modules.social.presentation.schemas.report_schemas import ReportRequest

        request = ReportRequest(
            reported_user_id=reported_user_id,
            reason=ReportReason.FRAUD,
            detail="Suspected scam",
        )
        mock_session = AsyncMock()

        mock_report_entity.reason = ReportReason.FRAUD
        mock_report_entity.detail = "Suspected scam"
        mock_report_use_case.execute.return_value = mock_report_entity

        # Act
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportUserUseCase",
            return_value=mock_report_use_case,
        ):
            result = await submit_report(
                request=request,
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        assert result.data.reason == ReportReason.FRAUD
        assert result.data.detail == "Suspected scam"

    @pytest.mark.asyncio
    async def test_submit_report_without_detail(
        self, mock_report_use_case, mock_report_entity, current_user_id, reported_user_id
    ):
        """Test submitting a report without detail description"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import submit_report
        from app.modules.social.presentation.schemas.report_schemas import ReportRequest

        request = ReportRequest(
            reported_user_id=reported_user_id,
            reason=ReportReason.SPAM,
            detail=None,
        )
        mock_session = AsyncMock()

        mock_report_entity.reason = ReportReason.SPAM
        mock_report_entity.detail = None
        mock_report_use_case.execute.return_value = mock_report_entity

        # Act
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportUserUseCase",
            return_value=mock_report_use_case,
        ):
            result = await submit_report(
                request=request,
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        assert result.data.reason == ReportReason.SPAM
        assert result.data.detail is None

    @pytest.mark.asyncio
    async def test_submit_report_validation_error(
        self, mock_report_use_case, current_user_id, reported_user_id
    ):
        """Test submitting report with validation error (e.g., reporting yourself)"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import submit_report
        from app.modules.social.presentation.schemas.report_schemas import ReportRequest

        request = ReportRequest(
            reported_user_id=reported_user_id,
            reason=ReportReason.HARASSMENT,
            detail="Test",
        )
        mock_session = AsyncMock()

        mock_report_use_case.execute.side_effect = ValueError("Cannot report yourself")

        # Act & Assert
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportUserUseCase",
            return_value=mock_report_use_case,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await submit_report(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 422
            assert "Cannot report yourself" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_report_internal_error(
        self, mock_report_use_case, current_user_id, reported_user_id
    ):
        """Test submitting report with internal server error"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import submit_report
        from app.modules.social.presentation.schemas.report_schemas import ReportRequest

        request = ReportRequest(
            reported_user_id=reported_user_id,
            reason=ReportReason.FRAUD,
            detail="Test",
        )
        mock_session = AsyncMock()

        mock_report_use_case.execute.side_effect = Exception("Database error")

        # Act & Assert
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportUserUseCase",
            return_value=mock_report_use_case,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await submit_report(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 500
            assert "Failed to submit report" in str(exc_info.value.detail)

    # Get My Reports Tests

    @pytest.mark.asyncio
    async def test_get_my_reports_success(
        self, mock_report_repo, mock_report_entity, current_user_id
    ):
        """Test successfully retrieving user's reports"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import get_my_reports

        mock_session = AsyncMock()
        mock_report_repo.find_by_reporter.return_value = [mock_report_entity]

        # Act
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportRepositoryImpl",
            return_value=mock_report_repo,
        ):
            result = await get_my_reports(
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        assert result.data.total == 1
        assert len(result.data.reports) == 1
        assert result.data.reports[0].reason == ReportReason.HARASSMENT
        assert result.error is None
        mock_report_repo.find_by_reporter.assert_called_once_with(str(current_user_id))

    @pytest.mark.asyncio
    async def test_get_my_reports_empty_list(self, mock_report_repo, current_user_id):
        """Test retrieving reports when user has no reports"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import get_my_reports

        mock_session = AsyncMock()
        mock_report_repo.find_by_reporter.return_value = []

        # Act
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportRepositoryImpl",
            return_value=mock_report_repo,
        ):
            result = await get_my_reports(
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        assert result.data.total == 0
        assert len(result.data.reports) == 0
        assert result.error is None

    @pytest.mark.asyncio
    async def test_get_my_reports_multiple(
        self, mock_report_repo, mock_report_entity, current_user_id
    ):
        """Test retrieving multiple reports"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import get_my_reports

        mock_session = AsyncMock()

        # Create multiple report entities
        mock_report_entity2 = AsyncMock()
        mock_report_entity2.id = str(uuid4())
        mock_report_entity2.reporter_id = str(current_user_id)
        mock_report_entity2.reported_user_id = str(uuid4())
        mock_report_entity2.reason = ReportReason.SPAM
        mock_report_entity2.detail = "Spam report"
        mock_report_entity2.created_at = datetime.utcnow()

        mock_report_repo.find_by_reporter.return_value = [
            mock_report_entity,
            mock_report_entity2,
        ]

        # Act
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportRepositoryImpl",
            return_value=mock_report_repo,
        ):
            result = await get_my_reports(
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        assert result.data.total == 2
        assert len(result.data.reports) == 2
        assert result.data.reports[0].reason == ReportReason.HARASSMENT
        assert result.data.reports[1].reason == ReportReason.SPAM

    @pytest.mark.asyncio
    async def test_get_my_reports_internal_error(self, mock_report_repo, current_user_id):
        """Test getting reports with internal server error"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import get_my_reports

        mock_session = AsyncMock()
        mock_report_repo.find_by_reporter.side_effect = Exception("Database error")

        # Act & Assert
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportRepositoryImpl",
            return_value=mock_report_repo,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_my_reports(
                    current_user_id=current_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 500
            assert "Failed to get reports" in str(exc_info.value.detail)

    # Edge Cases

    @pytest.mark.asyncio
    async def test_submit_report_creates_repository_correctly(
        self, mock_report_use_case, mock_report_entity, current_user_id, reported_user_id
    ):
        """Test that submit_report creates repository with correct session"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import submit_report
        from app.modules.social.presentation.schemas.report_schemas import ReportRequest

        request = ReportRequest(
            reported_user_id=reported_user_id,
            reason=ReportReason.FRAUD,
            detail="Test",
        )
        mock_session = AsyncMock()

        mock_report_use_case.execute.return_value = mock_report_entity
        mock_repo_class = AsyncMock()

        # Act
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportUserUseCase",
            return_value=mock_report_use_case,
        ):
            with patch(
                "app.modules.social.presentation.routers.report_router.ReportRepositoryImpl",
                mock_repo_class,
            ):
                await submit_report(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

        # Assert
        mock_repo_class.assert_called_once_with(mock_session)

    @pytest.mark.asyncio
    async def test_get_my_reports_creates_repository_correctly(
        self, mock_report_repo, current_user_id
    ):
        """Test that get_my_reports creates repository with correct session"""
        # Arrange
        from app.modules.social.presentation.routers.report_router import get_my_reports

        mock_session = AsyncMock()
        mock_report_repo.find_by_reporter.return_value = []
        mock_repo_class = AsyncMock(return_value=mock_report_repo)

        # Act
        with patch(
            "app.modules.social.presentation.routers.report_router.ReportRepositoryImpl",
            mock_repo_class,
        ):
            await get_my_reports(
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        mock_repo_class.assert_called_once_with(mock_session)
