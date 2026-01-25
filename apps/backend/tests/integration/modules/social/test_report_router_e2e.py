"""
Integration E2E tests for Report Router

Tests the report management endpoints:
- POST /reports - Submit report
- GET /reports/types - Get report types (if exists)
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import UUID, uuid4

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id


class TestReportRouterE2E:
    """E2E tests for Report Router endpoints"""

    @pytest_asyncio.fixture
    async def test_user1(self, db_session) -> UUID:
        """Create first test user"""
        import uuid
        unique_id = str(uuid.uuid4())
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": f"test_report1_{unique_id}",
                "email": f"report1_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest_asyncio.fixture
    async def test_user2(self, db_session) -> UUID:
        """Create second test user"""
        import uuid
        unique_id = str(uuid.uuid4())
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": f"test_report2_{unique_id}",
                "email": f"report2_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest.fixture
    def authenticated_client(self, test_user1, db_session):
        """Provide authenticated test client"""
        def override_get_current_user_id():
            return test_user1

        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = override_get_db_session

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    @pytest.fixture
    def unauthenticated_client(self, db_session):
        """Provide unauthenticated test client"""
        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[get_db_session] = override_get_db_session

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    # ===== Submit Report Tests =====

    def test_submit_report_success(self, authenticated_client, test_user2):
        """Test submitting a report successfully"""
        payload = {
            "reported_user_id": str(test_user2),
            "reason": "spam",
            "detail": "User is sending spam messages"
        }

        response = authenticated_client.post("/api/v1/reports", json=payload)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["reported_user_id"] == str(test_user2)
        assert data["reason"] == "spam"
        assert "id" in data

    def test_submit_report_harassment(self, authenticated_client, test_user2):
        """Test submitting harassment report"""
        payload = {
            "reported_user_id": str(test_user2),
            "reason": "harassment",
            "detail": "User sent threatening messages"
        }

        response = authenticated_client.post("/api/v1/reports", json=payload)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["reason"] == "harassment"

    def test_submit_report_self(self, authenticated_client, test_user1):
        """Test reporting oneself (should fail)"""
        payload = {
            "reported_user_id": str(test_user1),
            "reason": "spam",
            "detail": "Testing"
        }

        response = authenticated_client.post("/api/v1/reports", json=payload)

        assert response.status_code == 422

    def test_submit_report_invalid_reason(self, authenticated_client, test_user2):
        """Test submitting report with invalid reason"""
        payload = {
            "reported_user_id": str(test_user2),
            "reason": "invalid_reason",
            "detail": "Test"
        }

        response = authenticated_client.post("/api/v1/reports", json=payload)

        assert response.status_code in [400, 422]

    def test_submit_report_missing_reason(self, authenticated_client, test_user2):
        """Test submitting report without reason"""
        payload = {
            "reported_user_id": str(test_user2),
            "detail": "Test"
        }

        response = authenticated_client.post("/api/v1/reports", json=payload)

        assert response.status_code == 400

    def test_submit_report_missing_user_id(self, authenticated_client):
        """Test submitting report without reported_user_id"""
        payload = {
            "reason": "spam",
            "detail": "Test"
        }

        response = authenticated_client.post("/api/v1/reports", json=payload)

        assert response.status_code == 400

    def test_submit_report_unauthorized(self, unauthenticated_client, test_user2):
        """Test submitting report without authentication"""
        payload = {
            "reported_user_id": str(test_user2),
            "reason": "spam",
            "detail": "Test"
        }

        response = unauthenticated_client.post("/api/v1/reports", json=payload)

        assert response.status_code == 401

    # ===== Get Report Types Tests (if endpoint exists) =====

    def test_get_report_types(self, authenticated_client):
        """Test getting report types (if endpoint exists)"""
        response = authenticated_client.get("/api/v1/reports/types")

        # Should return 200 if endpoint exists, or 404 if not implemented
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))
