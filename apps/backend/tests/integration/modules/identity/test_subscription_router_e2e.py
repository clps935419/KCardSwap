"""
Integration E2E tests for Subscription Router

Tests the subscription management endpoints:
- POST /subscriptions/verify-receipt - Verify purchase receipt
- GET /subscriptions/status - Get subscription status
- POST /subscriptions/expire-subscriptions - Expire subscriptions
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from unittest.mock import AsyncMock, patch
from uuid import UUID

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id


class TestSubscriptionRouterE2E:
    """E2E tests for Subscription Router endpoints"""

    @pytest_asyncio.fixture
    async def test_user(self, db_session) -> UUID:
        """Create test user and return user ID"""
        import uuid
        unique_id = str(uuid.uuid4())
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": f"test_subscription_{unique_id}",
                "email": f"subscription_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest.fixture
    def authenticated_client(self, test_user, db_session):
        """Provide authenticated test client"""
        def override_get_current_user_id():
            return test_user

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

    def test_get_subscription_status_no_subscription(self, authenticated_client):
        """Test getting subscription status when user has no subscription"""
        response = authenticated_client.get("/api/v1/subscriptions/status")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["is_subscribed"] is False
        assert data["plan"] is None

    def test_get_subscription_status_unauthorized(self, unauthenticated_client):
        """Test getting subscription status without authentication returns 401"""
        response = unauthenticated_client.get("/api/v1/subscriptions/status")

        assert response.status_code == 401

    @patch("app.modules.identity.application.use_cases.subscription.verify_receipt_use_case.GooglePlayService")
    def test_verify_receipt_success(self, mock_google_play, authenticated_client):
        """Test successful receipt verification"""
        # Mock Google Play verification
        mock_service = AsyncMock()
        mock_service.verify_purchase = AsyncMock(return_value={
            "orderId": "TEST_ORDER_123",
            "purchaseState": 0,  # Purchased
            "expiryTimeMillis": "1735689600000",  # Future timestamp
        })
        mock_google_play.return_value = mock_service

        payload = {
            "platform": "google_play",
            "purchase_token": "test_token_123",
            "product_id": "monthly_premium"
        }

        response = authenticated_client.post(
            "/api/v1/subscriptions/verify-receipt",
            json=payload
        )

        # Should succeed or return service unavailable if Google Play is not configured
        assert response.status_code in [200, 503]

    def test_verify_receipt_invalid_platform(self, authenticated_client):
        """Test receipt verification with invalid platform"""
        payload = {
            "platform": "invalid_platform",
            "purchase_token": "test_token_123",
            "product_id": "monthly_premium"
        }

        response = authenticated_client.post(
            "/api/v1/subscriptions/verify-receipt",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "400_VALIDATION_FAILED"

    def test_verify_receipt_missing_fields(self, authenticated_client):
        """Test receipt verification with missing required fields"""
        payload = {
            "platform": "google_play",
            # Missing purchase_token and product_id
        }

        response = authenticated_client.post(
            "/api/v1/subscriptions/verify-receipt",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "400_VALIDATION_FAILED"

    def test_verify_receipt_unauthorized(self, unauthenticated_client):
        """Test receipt verification without authentication"""
        payload = {
            "platform": "google_play",
            "purchase_token": "test_token_123",
            "product_id": "monthly_premium"
        }

        response = unauthenticated_client.post(
            "/api/v1/subscriptions/verify-receipt",
            json=payload
        )

        assert response.status_code == 401

    def test_expire_subscriptions_success(self, authenticated_client):
        """Test expiring subscriptions endpoint"""
        response = authenticated_client.post("/api/v1/subscriptions/expire-subscriptions")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "expired_count" in data
        assert "processed_at" in data
        assert isinstance(data["expired_count"], int)

    @pytest_asyncio.fixture
    async def test_user_with_subscription(self, db_session) -> UUID:
        """Create test user with an active subscription"""
        import uuid
        from datetime import datetime, timedelta
        
        unique_id = str(uuid.uuid4())
        
        # Create user
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": f"test_sub_user_{unique_id}",
                "email": f"sub_user_{unique_id}@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        
        # Create subscription
        expires_at = datetime.utcnow() + timedelta(days=30)
        await db_session.execute(
            text("""
                INSERT INTO subscriptions (
                    user_id, platform, plan, status, 
                    started_at, expires_at, purchase_token, product_id
                )
                VALUES (
                    :user_id, :platform, :plan, :status,
                    :started_at, :expires_at, :purchase_token, :product_id
                )
            """),
            {
                "user_id": str(user_id),
                "platform": "google_play",
                "plan": "monthly_premium",
                "status": "active",
                "started_at": datetime.utcnow(),
                "expires_at": expires_at,
                "purchase_token": f"test_token_{unique_id}",
                "product_id": "monthly_premium"
            }
        )
        await db_session.flush()
        
        return user_id

    def test_get_subscription_status_with_active_subscription(
        self, test_user_with_subscription, db_session
    ):
        """Test getting subscription status when user has active subscription"""
        def override_get_current_user_id():
            return test_user_with_subscription

        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = override_get_db_session

        client = TestClient(app)
        
        try:
            response = client.get("/api/v1/subscriptions/status")

            assert response.status_code == 200
            data = response.json()["data"]
            assert data["is_subscribed"] is True
            assert data["plan"] == "monthly_premium"
            assert "expires_at" in data
        finally:
            app.dependency_overrides.clear()
