"""
Integration tests for Report Flow

Tests the complete report flow end-to-end including:
1. Submitting a report
2. Getting user's reports
3. Getting all reports (admin)
4. Validation and business rules
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.modules.social.domain.entities.report import Report, ReportReason

client = TestClient(app)


class TestReportFlowIntegration:
    """Integration tests for report flow"""

    @pytest.fixture
    def test_user_ids(self):
        """Generate test user IDs"""
        return {
            "reporter": uuid4(),
            "reported": uuid4(),
        }

    @pytest.fixture
    def test_report(self, test_user_ids):
        """Generate test report"""
        return Report(
            id=str(uuid4()),
            reporter_id=str(test_user_ids["reporter"]),
            reported_user_id=str(test_user_ids["reported"]),
            reason=ReportReason.HARASSMENT,
            detail="User sent threatening messages",
            created_at=datetime.utcnow(),
            resolved=False,
        )

    @pytest.fixture
    def test_reports(self, test_user_ids):
        """Generate multiple test reports"""
        return [
            Report(
                id=str(uuid4()),
                reporter_id=str(test_user_ids["reporter"]),
                reported_user_id=str(test_user_ids["reported"]),
                reason=ReportReason.HARASSMENT,
                detail="Harassment incident 1",
                created_at=datetime.utcnow(),
                resolved=False,
            ),
            Report(
                id=str(uuid4()),
                reporter_id=str(test_user_ids["reporter"]),
                reported_user_id=str(uuid4()),
                reason=ReportReason.SPAM,
                detail="Spam messages",
                created_at=datetime.utcnow(),
                resolved=False,
            ),
        ]

    @pytest.fixture
    def mock_auth_reporter(self, test_user_ids):
        """Mock authentication for reporter"""
        with patch(
            "app.modules.social.presentation.routers.report_router.get_current_user_id",
            return_value=test_user_ids["reporter"],
        ):
            yield test_user_ids["reporter"]

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        with patch(
            "app.modules.social.presentation.routers.report_router.get_db_session"
        ) as mock:
            session = Mock()
            mock.return_value = session
            yield session

    @pytest.mark.asyncio
    async def test_submit_report_harassment_success(
        self, mock_auth_reporter, mock_db_session, test_user_ids, test_report
    ):
        """Test successfully submitting a harassment report"""
        # Arrange
        from app.modules.social.infrastructure.repositories.report_repository_impl import (
            ReportRepositoryImpl,
        )

        with patch.object(
            ReportRepositoryImpl, "create", new_callable=AsyncMock
        ) as mock_create:

            def create_side_effect(report):
                return report

            mock_create.side_effect = create_side_effect

            # Act
            response = client.post(
                "/api/v1/reports",
                json={
                    "reported_user_id": str(test_user_ids["reported"]),
                    "reason": "harassment",  # Should use enum value
                    "detail": "User sent threatening messages",
                },
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["reported_user_id"] == str(test_user_ids["reported"])
            assert data["reason"] == "harassment"
            assert data["detail"] == "User sent threatening messages"
            assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_submit_report_all_valid_reasons(
        self, mock_auth_reporter, mock_db_session, test_user_ids
    ):
        """Test submitting reports with all valid reasons"""
        # Arrange
        from app.modules.social.infrastructure.repositories.report_repository_impl import (
            ReportRepositoryImpl,
        )

        with patch.object(
            ReportRepositoryImpl, "create", new_callable=AsyncMock
        ) as mock_create:

            def create_side_effect(report):
                return report

            mock_create.side_effect = create_side_effect

            valid_reasons = [
                "fraud",
                "fake_card",
                "harassment",
                "inappropriate_content",
                "spam",
                "other",
            ]

            for reason in valid_reasons:
                # Act
                response = client.post(
                    "/api/v1/reports",
                    json={
                        "reported_user_id": str(test_user_ids["reported"]),
                        "reason": reason,
                        "detail": f"Test report for {reason}",
                    },
                )

                # Assert
                assert (
                    response.status_code == status.HTTP_201_CREATED
                ), f"Failed for reason: {reason}"
                data = response.json()
                assert data["reason"] == reason

    @pytest.mark.asyncio
    async def test_submit_report_without_detail(
        self, mock_auth_reporter, mock_db_session, test_user_ids
    ):
        """Test submitting report without detail (optional)"""
        # Arrange
        from app.modules.social.infrastructure.repositories.report_repository_impl import (
            ReportRepositoryImpl,
        )

        with patch.object(
            ReportRepositoryImpl, "create", new_callable=AsyncMock
        ) as mock_create:

            def create_side_effect(report):
                return report

            mock_create.side_effect = create_side_effect

            # Act
            response = client.post(
                "/api/v1/reports",
                json={
                    "reported_user_id": str(test_user_ids["reported"]),
                    "reason": "spam",
                },
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["detail"] is None or data["detail"] == ""

    @pytest.mark.asyncio
    async def test_submit_report_invalid_reason_fails(
        self, mock_auth_reporter, mock_db_session, test_user_ids
    ):
        """Test submitting report with invalid reason fails"""
        # Act
        response = client.post(
            "/api/v1/reports",
            json={
                "reported_user_id": str(test_user_ids["reported"]),
                "reason": "invalid_reason",  # Not a valid enum value
                "detail": "Test",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_submit_report_self_report_fails(
        self, mock_auth_reporter, mock_db_session, test_user_ids
    ):
        """Test cannot report yourself"""
        # Act
        response = client.post(
            "/api/v1/reports",
            json={
                "reported_user_id": str(test_user_ids["reporter"]),  # Same as reporter
                "reason": "spam",
                "detail": "Test",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_get_my_reports_success(
        self, mock_auth_reporter, mock_db_session, test_user_ids, test_reports
    ):
        """Test successfully getting user's own reports"""
        # Arrange
        from app.modules.social.infrastructure.repositories.report_repository_impl import (
            ReportRepositoryImpl,
        )

        with patch.object(
            ReportRepositoryImpl, "find_by_reporter", new_callable=AsyncMock
        ) as mock_find:
            mock_find.return_value = test_reports

            # Act
            response = client.get("/api/v1/reports")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "reports" in data
            assert len(data["reports"]) == 2
            assert data["reports"][0]["reason"] in ["harassment", "spam"]

    @pytest.mark.asyncio
    async def test_get_my_reports_empty(
        self, mock_auth_reporter, mock_db_session, test_user_ids
    ):
        """Test getting reports when user has no reports"""
        # Arrange
        from app.modules.social.infrastructure.repositories.report_repository_impl import (
            ReportRepositoryImpl,
        )

        with patch.object(
            ReportRepositoryImpl, "find_by_reporter", new_callable=AsyncMock
        ) as mock_find:
            mock_find.return_value = []

            # Act
            response = client.get("/api/v1/reports")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["reports"] == []
            assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_report_detail_too_long_fails(
        self, mock_auth_reporter, mock_db_session, test_user_ids
    ):
        """Test report with detail exceeding max length fails"""
        # Arrange
        long_detail = "x" * 2001  # Exceeds 2000 char limit

        # Act
        response = client.post(
            "/api/v1/reports",
            json={
                "reported_user_id": str(test_user_ids["reported"]),
                "reason": "other",
                "detail": long_detail,
            },
        )

        # Assert
        # Should fail validation either at schema level (422) or use case level (500)
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    @pytest.mark.asyncio
    async def test_report_detail_at_max_length_success(
        self, mock_auth_reporter, mock_db_session, test_user_ids
    ):
        """Test report with detail at maximum length succeeds"""
        # Arrange
        from app.modules.social.infrastructure.repositories.report_repository_impl import (
            ReportRepositoryImpl,
        )

        with patch.object(
            ReportRepositoryImpl, "create", new_callable=AsyncMock
        ) as mock_create:

            def create_side_effect(report):
                return report

            mock_create.side_effect = create_side_effect

            max_detail = "x" * 1000  # Schema max is 1000

            # Act
            response = client.post(
                "/api/v1/reports",
                json={
                    "reported_user_id": str(test_user_ids["reported"]),
                    "reason": "other",
                    "detail": max_detail,
                },
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert len(data["detail"]) == 1000
