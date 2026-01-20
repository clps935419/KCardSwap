"""
Unit tests for ReportUserUseCase

Tests the report use case implementation with mocked repositories.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.reports.report_user_use_case import (
    ReportUserUseCase,
)
from app.modules.social.domain.entities.report import ReportReason


class TestReportUserUseCase:
    """Test ReportUserUseCase"""

    @pytest.fixture
    def mock_report_repository(self):
        """Create mock report repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_report_repository):
        """Create use case instance"""
        return ReportUserUseCase(report_repository=mock_report_repository)

    @pytest.mark.asyncio
    async def test_report_user_success_with_fraud(
        self, use_case, mock_report_repository
    ):
        """Test successful report creation for fraud"""
        # Arrange
        reporter_id = str(uuid4())
        reported_user_id = str(uuid4())
        reason = ReportReason.FRAUD
        detail = "User attempted to trade fake cards"

        # Mock report creation
        def create_side_effect(report):
            return report

        mock_report_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            detail=detail,
        )

        # Assert
        assert result is not None
        assert result.reporter_id == reporter_id
        assert result.reported_user_id == reported_user_id
        assert result.reason == reason
        assert result.detail == detail
        assert result.resolved is False

        # Verify repository calls
        mock_report_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_report_user_success_with_harassment(
        self, use_case, mock_report_repository
    ):
        """Test successful report creation for harassment"""
        # Arrange
        reporter_id = str(uuid4())
        reported_user_id = str(uuid4())
        reason = ReportReason.HARASSMENT
        detail = "User sent threatening messages"

        # Mock report creation
        def create_side_effect(report):
            return report

        mock_report_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            detail=detail,
        )

        # Assert
        assert result is not None
        assert result.reason == reason
        assert result.is_serious_violation()  # Harassment is serious
        mock_report_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_report_user_success_without_detail(
        self, use_case, mock_report_repository
    ):
        """Test successful report creation without detail"""
        # Arrange
        reporter_id = str(uuid4())
        reported_user_id = str(uuid4())
        reason = ReportReason.SPAM

        # Mock report creation
        def create_side_effect(report):
            return report

        mock_report_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            detail=None,
        )

        # Assert
        assert result is not None
        assert result.detail is None
        mock_report_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_report_user_cannot_report_self(
        self, use_case, mock_report_repository
    ):
        """Test cannot report yourself"""
        # Arrange
        user_id = str(uuid4())
        reason = ReportReason.SPAM

        # Act & Assert
        with pytest.raises(ValueError, match="User cannot report themselves"):
            await use_case.execute(
                reporter_id=user_id,
                reported_user_id=user_id,
                reason=reason,
                detail=None,
            )

        # Verify create was not called
        mock_report_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_report_user_detail_too_long(self, use_case, mock_report_repository):
        """Test report validation: detail too long"""
        # Arrange
        reporter_id = str(uuid4())
        reported_user_id = str(uuid4())
        reason = ReportReason.OTHER
        long_detail = "x" * 2001  # Exceeds 2000 char limit

        # Act & Assert
        with pytest.raises(
            ValueError, match="Report detail exceeds maximum length of 2000 characters"
        ):
            await use_case.execute(
                reporter_id=reporter_id,
                reported_user_id=reported_user_id,
                reason=reason,
                detail=long_detail,
            )

        # Verify create was not called
        mock_report_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_report_user_detail_at_max_length(
        self, use_case, mock_report_repository
    ):
        """Test successful report with detail at maximum length"""
        # Arrange
        reporter_id = str(uuid4())
        reported_user_id = str(uuid4())
        reason = ReportReason.OTHER
        max_detail = "x" * 2000  # Exactly at 2000 char limit

        # Mock report creation
        def create_side_effect(report):
            return report

        mock_report_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            detail=max_detail,
        )

        # Assert
        assert result is not None
        assert result.detail == max_detail
        mock_report_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_report_user_all_report_reasons(
        self, use_case, mock_report_repository
    ):
        """Test all valid report reasons"""
        # Arrange
        reporter_id = str(uuid4())
        reported_user_id = str(uuid4())

        # Mock report creation
        def create_side_effect(report):
            return report

        mock_report_repository.create.side_effect = create_side_effect

        # Act & Assert - test all report reasons
        all_reasons = [
            ReportReason.FRAUD,
            ReportReason.FAKE_CARD,
            ReportReason.HARASSMENT,
            ReportReason.INAPPROPRIATE_CONTENT,
            ReportReason.SPAM,
            ReportReason.OTHER,
        ]

        for reason in all_reasons:
            result = await use_case.execute(
                reporter_id=reporter_id,
                reported_user_id=reported_user_id,
                reason=reason,
                detail=f"Report for {reason.value}",
            )
            assert result.reason == reason

        # Verify create was called for each reason
        assert mock_report_repository.create.call_count == len(all_reasons)

    @pytest.mark.asyncio
    async def test_report_user_serious_violations(
        self, use_case, mock_report_repository
    ):
        """Test identification of serious violations"""
        # Arrange
        reporter_id = str(uuid4())
        reported_user_id = str(uuid4())

        # Mock report creation
        def create_side_effect(report):
            return report

        mock_report_repository.create.side_effect = create_side_effect

        # Test serious violations
        serious_reasons = [
            ReportReason.FRAUD,
            ReportReason.FAKE_CARD,
            ReportReason.HARASSMENT,
        ]

        for reason in serious_reasons:
            result = await use_case.execute(
                reporter_id=reporter_id,
                reported_user_id=reported_user_id,
                reason=reason,
                detail="Serious violation",
            )
            assert result.is_serious_violation() is True

        # Test non-serious violations
        non_serious_reasons = [
            ReportReason.SPAM,
            ReportReason.INAPPROPRIATE_CONTENT,
            ReportReason.OTHER,
        ]

        for reason in non_serious_reasons:
            result = await use_case.execute(
                reporter_id=reporter_id,
                reported_user_id=reported_user_id,
                reason=reason,
                detail="Non-serious violation",
            )
            assert result.is_serious_violation() is False

    @pytest.mark.asyncio
    async def test_report_user_initial_state(self, use_case, mock_report_repository):
        """Test that new reports have correct initial state"""
        # Arrange
        reporter_id = str(uuid4())
        reported_user_id = str(uuid4())
        reason = ReportReason.SPAM

        # Mock report creation
        def create_side_effect(report):
            return report

        mock_report_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            detail="Test report",
        )

        # Assert initial state
        assert result.resolved is False
        assert result.resolved_at is None
        assert result.created_at is not None
        mock_report_repository.create.assert_called_once()
