"""
Unit tests for Subscription Router

Tests the subscription router endpoints.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.identity.presentation.routers.subscription_router import (
    expire_subscriptions,
    get_subscription_status,
    verify_receipt,
)
from app.modules.identity.presentation.schemas.subscription_schemas import (
    VerifyReceiptRequest,
)


class TestSubscriptionRouter:
    """Test Subscription Router endpoints"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        session = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def mock_verify_receipt_use_case(self):
        """Create mock verify receipt use case"""
        use_case = AsyncMock()
        use_case.execute = AsyncMock()
        return use_case

    @pytest.fixture
    def mock_check_status_use_case(self):
        """Create mock check subscription status use case"""
        use_case = AsyncMock()
        use_case.execute = AsyncMock()
        return use_case

    @pytest.fixture
    def mock_expire_subscriptions_use_case(self):
        """Create mock expire subscriptions use case"""
        use_case = AsyncMock()
        use_case.execute = AsyncMock()
        return use_case

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.mark.asyncio
    async def test_verify_receipt_success(
        self,
        mock_session,
        mock_verify_receipt_use_case,
        sample_user_id,
    ):
        """Test verify receipt endpoint with successful verification"""
        # Arrange
        request = VerifyReceiptRequest(
            platform="google_play",
            purchase_token="test_token_123",
            product_id="premium_monthly",
        )

        expected_result = {
            "plan": "premium",
            "status": "active",
            "expires_at": "2024-12-31T23:59:59Z",
            "entitlement_active": True,
            "source": "google_play",
        }
        mock_verify_receipt_use_case.execute.return_value = expected_result

        # Act
        response = await verify_receipt(
            request=request,
            session=mock_session,
            use_case=mock_verify_receipt_use_case,
            current_user_id=sample_user_id,
        )

        # Assert
        assert response.data.plan == "premium"
        assert response.data.status == "active"
        assert response.data.entitlement_active is True
        assert response.data.source == "google_play"
        assert response.meta is None
        assert response.error is None
        mock_verify_receipt_use_case.execute.assert_called_once_with(
            user_id=sample_user_id,
            platform="google_play",
            purchase_token="test_token_123",
            product_id="premium_monthly",
        )
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_receipt_idempotent(
        self,
        mock_session,
        mock_verify_receipt_use_case,
        sample_user_id,
    ):
        """Test verify receipt is idempotent for same token"""
        # Arrange
        request = VerifyReceiptRequest(
            platform="google_play",
            purchase_token="same_token",
            product_id="premium_monthly",
        )

        expected_result = {
            "plan": "premium",
            "status": "active",
            "expires_at": "2024-12-31T23:59:59Z",
            "entitlement_active": True,
            "source": "google_play",
        }
        mock_verify_receipt_use_case.execute.return_value = expected_result

        # Act - Call twice with same token
        response1 = await verify_receipt(
            request=request,
            session=mock_session,
            use_case=mock_verify_receipt_use_case,
            current_user_id=sample_user_id,
        )
        response2 = await verify_receipt(
            request=request,
            session=mock_session,
            use_case=mock_verify_receipt_use_case,
            current_user_id=sample_user_id,
        )

        # Assert
        assert response1.data.plan == response2.data.plan
        assert response1.data.entitlement_active == response2.data.entitlement_active
        assert mock_verify_receipt_use_case.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_verify_receipt_with_different_platforms(
        self,
        mock_session,
        mock_verify_receipt_use_case,
        sample_user_id,
    ):
        """Test verify receipt with different platform values"""
        # Arrange
        request_google = VerifyReceiptRequest(
            platform="google_play",
            purchase_token="google_token",
            product_id="premium_monthly",
        )

        expected_result = {
            "plan": "premium",
            "status": "active",
            "expires_at": "2024-12-31T23:59:59Z",
            "entitlement_active": True,
            "source": "google_play",
        }
        mock_verify_receipt_use_case.execute.return_value = expected_result

        # Act
        response = await verify_receipt(
            request=request_google,
            session=mock_session,
            use_case=mock_verify_receipt_use_case,
            current_user_id=sample_user_id,
        )

        # Assert
        assert response.data.source == "google_play"
        mock_verify_receipt_use_case.execute.assert_called_with(
            user_id=sample_user_id,
            platform="google_play",
            purchase_token="google_token",
            product_id="premium_monthly",
        )

    @pytest.mark.asyncio
    async def test_get_subscription_status_premium(
        self,
        mock_session,
        mock_check_status_use_case,
        sample_user_id,
    ):
        """Test get subscription status for premium user"""
        # Arrange
        expected_result = {
            "plan": "premium",
            "status": "active",
            "expires_at": "2024-12-31T23:59:59Z",
            "entitlement_active": True,
            "source": "google_play",
        }
        mock_check_status_use_case.execute.return_value = expected_result

        # Act
        response = await get_subscription_status(
            session=mock_session,
            use_case=mock_check_status_use_case,
            current_user_id=sample_user_id,
        )

        # Assert
        assert response.data.plan == "premium"
        assert response.data.status == "active"
        assert response.data.entitlement_active is True
        assert response.data.source == "google_play"
        assert response.meta is None
        assert response.error is None
        mock_check_status_use_case.execute.assert_called_once_with(
            user_id=sample_user_id
        )
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_subscription_status_free(
        self,
        mock_session,
        mock_check_status_use_case,
        sample_user_id,
    ):
        """Test get subscription status for free user"""
        # Arrange
        expected_result = {
            "plan": "free",
            "status": "inactive",
            "expires_at": None,
            "entitlement_active": False,
            "source": "none",
        }
        mock_check_status_use_case.execute.return_value = expected_result

        # Act
        response = await get_subscription_status(
            session=mock_session,
            use_case=mock_check_status_use_case,
            current_user_id=sample_user_id,
        )

        # Assert
        assert response.data.plan == "free"
        assert response.data.status == "inactive"
        assert response.data.entitlement_active is False
        assert response.data.expires_at is None

    @pytest.mark.asyncio
    async def test_expire_subscriptions_success(
        self,
        mock_session,
        mock_expire_subscriptions_use_case,
    ):
        """Test expire subscriptions endpoint"""
        # Arrange
        expected_result = {
            "expired_count": 5,
            "processed_at": "2024-01-24T12:00:00Z",
        }
        mock_expire_subscriptions_use_case.execute.return_value = expected_result

        # Act
        response = await expire_subscriptions(
            session=mock_session,
            use_case=mock_expire_subscriptions_use_case,
        )

        # Assert
        assert response.data.expired_count == 5
        assert response.data.processed_at == "2024-01-24T12:00:00Z"
        assert response.meta is None
        assert response.error is None
        mock_expire_subscriptions_use_case.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_expire_subscriptions_no_expired(
        self,
        mock_session,
        mock_expire_subscriptions_use_case,
    ):
        """Test expire subscriptions when no subscriptions need expiring"""
        # Arrange
        expected_result = {
            "expired_count": 0,
            "processed_at": "2024-01-24T12:00:00Z",
        }
        mock_expire_subscriptions_use_case.execute.return_value = expected_result

        # Act
        response = await expire_subscriptions(
            session=mock_session,
            use_case=mock_expire_subscriptions_use_case,
        )

        # Assert
        assert response.data.expired_count == 0

    @pytest.mark.asyncio
    async def test_verify_receipt_commits_session(
        self,
        mock_session,
        mock_verify_receipt_use_case,
        sample_user_id,
    ):
        """Test that verify receipt commits the session"""
        # Arrange
        request = VerifyReceiptRequest(
            platform="google_play",
            purchase_token="test_token",
            product_id="premium_monthly",
        )
        mock_verify_receipt_use_case.execute.return_value = {
            "plan": "premium",
            "status": "active",
            "expires_at": "2024-12-31T23:59:59Z",
            "entitlement_active": True,
            "source": "google_play",
        }

        # Act
        await verify_receipt(
            request=request,
            session=mock_session,
            use_case=mock_verify_receipt_use_case,
            current_user_id=sample_user_id,
        )

        # Assert
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_subscription_status_commits_session(
        self,
        mock_session,
        mock_check_status_use_case,
        sample_user_id,
    ):
        """Test that get subscription status commits the session"""
        # Arrange
        mock_check_status_use_case.execute.return_value = {
            "plan": "free",
            "status": "inactive",
            "expires_at": None,
            "entitlement_active": False,
            "source": "none",
        }

        # Act
        await get_subscription_status(
            session=mock_session,
            use_case=mock_check_status_use_case,
            current_user_id=sample_user_id,
        )

        # Assert
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_expire_subscriptions_commits_session(
        self,
        mock_session,
        mock_expire_subscriptions_use_case,
    ):
        """Test that expire subscriptions commits the session"""
        # Arrange
        mock_expire_subscriptions_use_case.execute.return_value = {
            "expired_count": 3,
            "processed_at": "2024-01-24T12:00:00Z",
        }

        # Act
        await expire_subscriptions(
            session=mock_session,
            use_case=mock_expire_subscriptions_use_case,
        )

        # Assert
        mock_session.commit.assert_called_once()


class TestVerifyReceiptRequest:
    """Test VerifyReceiptRequest schema"""

    def test_verify_receipt_request_creation(self):
        """Test creating VerifyReceiptRequest"""
        # Act
        request = VerifyReceiptRequest(
            platform="google_play",
            purchase_token="test_token",
            product_id="premium_monthly",
        )

        # Assert
        assert request.platform == "google_play"
        assert request.purchase_token == "test_token"
        assert request.product_id == "premium_monthly"

    def test_verify_receipt_request_serialization(self):
        """Test VerifyReceiptRequest serialization"""
        # Arrange
        request = VerifyReceiptRequest(
            platform="google_play",
            purchase_token="test_token",
            product_id="premium_monthly",
        )

        # Act
        data = request.model_dump()

        # Assert
        assert data["platform"] == "google_play"
        assert data["purchase_token"] == "test_token"
        assert data["product_id"] == "premium_monthly"
