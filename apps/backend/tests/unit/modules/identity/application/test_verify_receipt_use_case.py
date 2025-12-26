"""
Unit tests for VerifyReceiptUseCase (T186)

Tests the Google Play receipt verification flow including:
- Token binding and replay attack prevention
- Idempotent behavior for same token + same user
- Cross-user replay rejection (409 CONFLICT)
- Google Play API integration
- Subscription status updates
- Purchase acknowledgment
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.modules.identity.application.use_cases.subscription.verify_receipt_use_case import (
    VerifyReceiptUseCase,
)
from app.modules.identity.domain.entities.subscription import Subscription
from app.shared.presentation.exceptions.api_exceptions import (
    ValidationException,
    ConflictException,
    ServiceUnavailableException,
)


@pytest.fixture
def mock_subscription_repo():
    """Mock subscription repository"""
    repo = Mock()
    repo.get_or_create_by_user_id = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_token_repo():
    """Mock purchase token repository"""
    repo = Mock()
    repo.get_user_id_for_token = AsyncMock(return_value=None)
    repo.bind_token_to_user = AsyncMock()
    return repo


@pytest.fixture
def mock_billing_service():
    """Mock Google Play Billing service"""
    service = Mock()
    service.verify_subscription_purchase = AsyncMock()
    service.acknowledge_subscription_purchase = AsyncMock(return_value=True)
    return service


@pytest.fixture
def sample_user_id():
    """Sample user UUID"""
    return uuid4()


@pytest.fixture
def sample_subscription(sample_user_id):
    """Sample free subscription"""
    return Subscription(
        id=1,
        user_id=sample_user_id,
        plan="free",
        status="inactive",
        expires_at=None,
    )


@pytest.fixture
def sample_premium_subscription(sample_user_id):
    """Sample premium subscription"""
    return Subscription(
        id=1,
        user_id=sample_user_id,
        plan="premium",
        status="active",
        expires_at=datetime.utcnow() + timedelta(days=30),
    )


@pytest.mark.asyncio
async def test_verify_receipt_success_new_purchase(
    mock_subscription_repo,
    mock_token_repo,
    mock_billing_service,
    sample_user_id,
    sample_subscription,
):
    """Test successful verification of a new purchase"""
    # Arrange
    purchase_token = "test_token_123"
    product_id = "premium_monthly"
    expires_at = datetime.utcnow() + timedelta(days=30)

    # Mock subscription repository
    mock_subscription_repo.get_or_create_by_user_id.return_value = sample_subscription
    updated_subscription = Subscription(
        id=1,
        user_id=sample_user_id,
        plan="premium",
        status="active",
        expires_at=expires_at,
    )
    mock_subscription_repo.update.return_value = updated_subscription

    # Mock Google Play verification (valid purchase)
    mock_billing_service.verify_subscription_purchase.return_value = {
        "is_valid": True,
        "expires_at": expires_at,
        "auto_renewing": True,
        "payment_state": 1,
        "acknowledgement_state": 0,
    }

    # Create use case
    use_case = VerifyReceiptUseCase(
        subscription_repository=mock_subscription_repo,
        purchase_token_repository=mock_token_repo,
        billing_service=mock_billing_service,
    )

    # Act
    result = await use_case.execute(
        user_id=sample_user_id,
        platform="android",
        purchase_token=purchase_token,
        product_id=product_id,
    )

    # Assert
    assert result["plan"] == "premium"
    assert result["status"] == "active"
    assert result["entitlement_active"] is True
    assert result["source"] == "google_play"

    # Verify token was bound
    mock_token_repo.bind_token_to_user.assert_called_once_with(
        purchase_token=purchase_token,
        user_id=sample_user_id,
        product_id=product_id,
        platform="android",
    )

    # Verify purchase was acknowledged
    mock_billing_service.acknowledge_subscription_purchase.assert_called_once()


@pytest.mark.asyncio
async def test_verify_receipt_idempotent_same_user(
    mock_subscription_repo,
    mock_token_repo,
    mock_billing_service,
    sample_user_id,
    sample_premium_subscription,
):
    """Test idempotent behavior when same user resends same token"""
    # Arrange
    purchase_token = "test_token_123"
    product_id = "premium_monthly"

    # Token already bound to this user
    mock_token_repo.get_user_id_for_token.return_value = sample_user_id
    mock_subscription_repo.get_or_create_by_user_id.return_value = (
        sample_premium_subscription
    )

    # Create use case
    use_case = VerifyReceiptUseCase(
        subscription_repository=mock_subscription_repo,
        purchase_token_repository=mock_token_repo,
        billing_service=mock_billing_service,
    )

    # Act
    result = await use_case.execute(
        user_id=sample_user_id,
        platform="android",
        purchase_token=purchase_token,
        product_id=product_id,
    )

    # Assert - should return current subscription status
    assert result["plan"] == "premium"
    assert result["status"] == "active"
    assert result["entitlement_active"] is True

    # Should NOT call Google Play API (idempotent)
    mock_billing_service.verify_subscription_purchase.assert_not_called()

    # Should NOT bind token again
    mock_token_repo.bind_token_to_user.assert_not_called()


@pytest.mark.asyncio
async def test_verify_receipt_reject_cross_user_replay(
    mock_subscription_repo,
    mock_token_repo,
    mock_billing_service,
    sample_user_id,
):
    """Test rejection of cross-user replay attack"""
    # Arrange
    purchase_token = "test_token_123"
    product_id = "premium_monthly"
    other_user_id = uuid4()

    # Token already bound to a DIFFERENT user
    mock_token_repo.get_user_id_for_token.return_value = other_user_id

    # Create use case
    use_case = VerifyReceiptUseCase(
        subscription_repository=mock_subscription_repo,
        purchase_token_repository=mock_token_repo,
        billing_service=mock_billing_service,
    )

    # Act & Assert
    with pytest.raises(ConflictException) as exc_info:
        await use_case.execute(
            user_id=sample_user_id,
            platform="android",
            purchase_token=purchase_token,
            product_id=product_id,
        )

    assert "PURCHASE_TOKEN_ALREADY_USED" in str(exc_info.value)
    assert "此購買已被其他帳號使用" in str(exc_info.value)


@pytest.mark.asyncio
async def test_verify_receipt_invalid_platform(
    mock_subscription_repo,
    mock_token_repo,
    mock_billing_service,
    sample_user_id,
):
    """Test validation of platform parameter"""
    # Arrange
    use_case = VerifyReceiptUseCase(
        subscription_repository=mock_subscription_repo,
        purchase_token_repository=mock_token_repo,
        billing_service=mock_billing_service,
    )

    # Act & Assert
    with pytest.raises(ValidationException) as exc_info:
        await use_case.execute(
            user_id=sample_user_id,
            platform="windows",  # Invalid platform
            purchase_token="test_token",
            product_id="premium_monthly",
        )

    assert "UNSUPPORTED_PLATFORM" in str(exc_info.value)


@pytest.mark.asyncio
async def test_verify_receipt_google_play_unavailable(
    mock_subscription_repo,
    mock_token_repo,
    mock_billing_service,
    sample_user_id,
    sample_subscription,
):
    """Test handling of Google Play API unavailability"""
    # Arrange
    mock_subscription_repo.get_or_create_by_user_id.return_value = sample_subscription

    # Mock Google Play API failure
    mock_billing_service.verify_subscription_purchase.side_effect = Exception(
        "Connection timeout"
    )

    # Create use case
    use_case = VerifyReceiptUseCase(
        subscription_repository=mock_subscription_repo,
        purchase_token_repository=mock_token_repo,
        billing_service=mock_billing_service,
    )

    # Act & Assert
    with pytest.raises(ServiceUnavailableException) as exc_info:
        await use_case.execute(
            user_id=sample_user_id,
            platform="android",
            purchase_token="test_token",
            product_id="premium_monthly",
        )

    assert "GOOGLE_PLAY_UNAVAILABLE" in str(exc_info.value)
    assert "驗證暫時失敗" in str(exc_info.value)


@pytest.mark.asyncio
async def test_verify_receipt_pending_payment(
    mock_subscription_repo,
    mock_token_repo,
    mock_billing_service,
    sample_user_id,
    sample_subscription,
):
    """Test handling of pending payment state"""
    # Arrange
    mock_subscription_repo.get_or_create_by_user_id.return_value = sample_subscription
    pending_subscription = Subscription(
        id=1,
        user_id=sample_user_id,
        plan="free",
        status="pending",
        expires_at=None,
    )
    mock_subscription_repo.update.return_value = pending_subscription

    # Mock Google Play verification (pending payment)
    mock_billing_service.verify_subscription_purchase.return_value = {
        "is_valid": False,
        "expires_at": None,
        "auto_renewing": False,
        "payment_state": 0,  # Pending
        "acknowledgement_state": 0,
    }

    # Create use case
    use_case = VerifyReceiptUseCase(
        subscription_repository=mock_subscription_repo,
        purchase_token_repository=mock_token_repo,
        billing_service=mock_billing_service,
    )

    # Act
    result = await use_case.execute(
        user_id=sample_user_id,
        platform="android",
        purchase_token="test_token",
        product_id="premium_monthly",
    )

    # Assert
    assert result["status"] == "pending"
    assert result["entitlement_active"] is False

    # Should update subscription status to pending
    mock_subscription_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_verify_receipt_acknowledge_failure_still_succeeds(
    mock_subscription_repo,
    mock_token_repo,
    mock_billing_service,
    sample_user_id,
    sample_subscription,
):
    """Test that acknowledgment failure doesn't fail the verification"""
    # Arrange
    expires_at = datetime.utcnow() + timedelta(days=30)
    mock_subscription_repo.get_or_create_by_user_id.return_value = sample_subscription
    updated_subscription = Subscription(
        id=1,
        user_id=sample_user_id,
        plan="premium",
        status="active",
        expires_at=expires_at,
    )
    mock_subscription_repo.update.return_value = updated_subscription

    # Mock Google Play verification (valid)
    mock_billing_service.verify_subscription_purchase.return_value = {
        "is_valid": True,
        "expires_at": expires_at,
        "auto_renewing": True,
        "payment_state": 1,
        "acknowledgement_state": 0,
    }

    # Mock acknowledgment failure
    mock_billing_service.acknowledge_subscription_purchase.side_effect = Exception(
        "Network error"
    )

    # Create use case
    use_case = VerifyReceiptUseCase(
        subscription_repository=mock_subscription_repo,
        purchase_token_repository=mock_token_repo,
        billing_service=mock_billing_service,
    )

    # Act - should not raise exception despite ack failure
    result = await use_case.execute(
        user_id=sample_user_id,
        platform="android",
        purchase_token="test_token",
        product_id="premium_monthly",
    )

    # Assert - subscription should still be activated
    assert result["plan"] == "premium"
    assert result["status"] == "active"
    assert result["entitlement_active"] is True
