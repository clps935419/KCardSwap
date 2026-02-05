"""
Unit tests for SubscriptionSchemas

Tests Pydantic model validation for subscription-related schemas.
"""

import pytest
from pydantic import ValidationError

from app.modules.identity.presentation.schemas.subscription_schemas import (
    ExpireSubscriptionsData,
    ExpireSubscriptionsResponse,
    SubscriptionStatusData,
    SubscriptionStatusResponse,
    VerifyReceiptRequest,
)


class TestSubscriptionStatusData:
    """Test SubscriptionStatusData schema"""

    def test_create_subscription_status_data_active(self):
        """Test creating active subscription status data"""
        # Arrange & Act
        subscription = SubscriptionStatusData(
            plan="premium",
            status="active",
            expires_at="2025-12-31T23:59:59",
            entitlement_active=True,
            source="google_play",
        )

        # Assert
        assert subscription.plan == "premium"
        assert subscription.status == "active"
        assert subscription.entitlement_active is True
        assert subscription.source == "google_play"

    def test_create_subscription_status_data_free(self):
        """Test creating free subscription status data"""
        # Arrange & Act
        subscription = SubscriptionStatusData(
            plan="free",
            status="active",
            expires_at=None,
            entitlement_active=False,
            source="google_play",
        )

        # Assert
        assert subscription.plan == "free"
        assert subscription.expires_at is None
        assert subscription.entitlement_active is False


class TestSubscriptionStatusResponse:
    """Test SubscriptionStatusResponse schema"""

    def test_create_subscription_status_response(self):
        """Test creating subscription status response"""
        # Arrange
        data = SubscriptionStatusData(
            plan="premium",
            status="active",
            expires_at="2025-12-31T23:59:59",
            entitlement_active=True,
            source="google_play",
        )

        # Act
        response = SubscriptionStatusResponse(data=data)

        # Assert
        assert response.data.plan == "premium"
        assert response.meta is None
        assert response.error is None


class TestVerifyReceiptRequest:
    """Test VerifyReceiptRequest schema"""

    def test_create_verify_receipt_request(self):
        """Test creating verify receipt request"""
        # Arrange & Act
        request = VerifyReceiptRequest(
            platform="android",
            purchase_token="abc123xyz",
            product_id="premium_monthly",
        )

        # Assert
        assert request.platform == "android"
        assert request.purchase_token == "abc123xyz"
        assert request.product_id == "premium_monthly"

    def test_verify_receipt_request_ios(self):
        """Test verify receipt request for iOS"""
        # Arrange & Act
        request = VerifyReceiptRequest(
            platform="ios",
            purchase_token="ios_token",
            product_id="premium_monthly",
        )

        # Assert
        assert request.platform == "ios"

    def test_verify_receipt_request_missing_fields(self):
        """Test verify receipt request fails without required fields"""
        # Act & Assert
        with pytest.raises(ValidationError):
            VerifyReceiptRequest(platform="android")  # type: ignore


class TestExpireSubscriptionsData:
    """Test ExpireSubscriptionsData schema"""

    def test_create_expire_subscriptions_data(self):
        """Test creating expire subscriptions data"""
        # Arrange & Act
        data = ExpireSubscriptionsData(
            expired_count=5,
            processed_at="2025-12-23T00:00:00",
        )

        # Assert
        assert data.expired_count == 5
        assert data.processed_at == "2025-12-23T00:00:00"


class TestExpireSubscriptionsResponse:
    """Test ExpireSubscriptionsResponse schema"""

    def test_create_expire_subscriptions_response(self):
        """Test creating expire subscriptions response"""
        # Arrange
        data = ExpireSubscriptionsData(
            expired_count=3,
            processed_at="2025-12-23T00:00:00",
        )

        # Act
        response = ExpireSubscriptionsResponse(data=data)

        # Assert
        assert response.data.expired_count == 3
        assert response.meta is None
        assert response.error is None
