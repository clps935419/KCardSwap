"""
Unit tests for Subscription Check Middleware
Testing subscription permission enforcement and request state injection
"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request

from app.shared.presentation.middleware.subscription_check import (
    check_subscription_permission,
    get_subscription_from_request,
    require_subscription_plan,
)


class MockSubscriptionInfo:
    """Mock subscription info object"""

    def __init__(self, plan_type="free", is_active=True):
        self.plan_type = plan_type
        self.is_active = is_active


class TestCheckSubscriptionPermission:
    """Test check_subscription_permission middleware"""

    @pytest.mark.asyncio
    async def test_no_authenticated_user_passes_through(self):
        """Test that requests without authenticated user pass through"""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.user = None

        mock_call_next = AsyncMock(return_value=Mock())

        response = await check_subscription_permission(mock_request, mock_call_next)

        assert response is not None
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_free_user_subscription_injected(self):
        """Test that free user subscription info is injected into request state"""
        user_id = uuid4()
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.user = {"id": str(user_id)}

        mock_call_next = AsyncMock(return_value=Mock())

        # Mock database session and subscription service
        mock_session = AsyncMock()
        mock_subscription_info = MockSubscriptionInfo(plan_type="free", is_active=True)

        async def mock_get_db_session():
            yield mock_session

        mock_subscription_service = AsyncMock()
        mock_subscription_service.get_or_create_subscription_info.return_value = (
            mock_subscription_info
        )

        with patch(
            "app.shared.presentation.middleware.subscription_check.get_db_session",
            return_value=mock_get_db_session(),
        ), patch(
            "app.shared.presentation.middleware.subscription_check.get_subscription_service",
            return_value=mock_subscription_service,
        ):
            response = await check_subscription_permission(mock_request, mock_call_next)

        assert response is not None
        assert hasattr(mock_request.state, "subscription")
        assert mock_request.state.subscription["plan"] == "free"
        assert mock_request.state.subscription["is_premium"] is False
        mock_call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_premium_user_subscription_injected(self):
        """Test that premium user subscription info is correctly injected"""
        user_id = uuid4()
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.user = {"id": str(user_id)}

        mock_call_next = AsyncMock(return_value=Mock())

        mock_session = AsyncMock()
        mock_subscription_info = MockSubscriptionInfo(
            plan_type="premium", is_active=True
        )

        async def mock_get_db_session():
            yield mock_session

        mock_subscription_service = AsyncMock()
        mock_subscription_service.get_or_create_subscription_info.return_value = (
            mock_subscription_info
        )

        with patch(
            "app.shared.presentation.middleware.subscription_check.get_db_session",
            return_value=mock_get_db_session(),
        ), patch(
            "app.shared.presentation.middleware.subscription_check.get_subscription_service",
            return_value=mock_subscription_service,
        ):
            response = await check_subscription_permission(mock_request, mock_call_next)

        assert response is not None
        assert mock_request.state.subscription["plan"] == "premium"
        assert mock_request.state.subscription["is_premium"] is True
        assert mock_request.state.subscription["entitlement_active"] is True

    @pytest.mark.asyncio
    async def test_inactive_subscription_marked_correctly(self):
        """Test that inactive subscription is marked as such"""
        user_id = uuid4()
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.user = {"id": user_id}

        mock_call_next = AsyncMock(return_value=Mock())

        mock_session = AsyncMock()
        mock_subscription_info = MockSubscriptionInfo(
            plan_type="premium", is_active=False
        )

        async def mock_get_db_session():
            yield mock_session

        mock_subscription_service = AsyncMock()
        mock_subscription_service.get_or_create_subscription_info.return_value = (
            mock_subscription_info
        )

        with patch(
            "app.shared.presentation.middleware.subscription_check.get_db_session",
            return_value=mock_get_db_session(),
        ), patch(
            "app.shared.presentation.middleware.subscription_check.get_subscription_service",
            return_value=mock_subscription_service,
        ):
            response = await check_subscription_permission(mock_request, mock_call_next)

        assert response is not None
        assert mock_request.state.subscription["status"] == "inactive"
        assert mock_request.state.subscription["is_premium"] is False
        assert mock_request.state.subscription["entitlement_active"] is False

    @pytest.mark.asyncio
    async def test_session_closed_after_processing(self):
        """Test that database session is properly closed"""
        user_id = uuid4()
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.user = {"id": str(user_id)}

        mock_call_next = AsyncMock(return_value=Mock())

        mock_session = AsyncMock()
        mock_subscription_info = MockSubscriptionInfo()

        async def mock_get_db_session():
            yield mock_session

        mock_subscription_service = AsyncMock()
        mock_subscription_service.get_or_create_subscription_info.return_value = (
            mock_subscription_info
        )

        with patch(
            "app.shared.presentation.middleware.subscription_check.get_db_session",
            return_value=mock_get_db_session(),
        ), patch(
            "app.shared.presentation.middleware.subscription_check.get_subscription_service",
            return_value=mock_subscription_service,
        ):
            await check_subscription_permission(mock_request, mock_call_next)

        mock_session.close.assert_called_once()


class TestRequireSubscriptionPlan:
    """Test require_subscription_plan dependency"""

    @pytest.mark.asyncio
    async def test_premium_required_with_premium_user_succeeds(self):
        """Test that premium user can access premium endpoint"""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.subscription = {
            "plan": "premium",
            "is_premium": True,
            "status": "active",
        }

        check_plan = require_subscription_plan("premium")
        # Should not raise
        await check_plan(mock_request)

    @pytest.mark.asyncio
    async def test_premium_required_with_free_user_fails(self):
        """Test that free user cannot access premium endpoint"""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.subscription = {
            "plan": "free",
            "is_premium": False,
            "status": "active",
        }

        check_plan = require_subscription_plan("premium")

        with pytest.raises(HTTPException) as exc_info:
            await check_plan(mock_request)

        assert exc_info.value.status_code == 403
        assert "PREMIUM_REQUIRED" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_no_subscription_info_raises_500(self):
        """Test that missing subscription info raises 500 error"""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock(spec=[])  # Empty spec means no attributes

        # Use spec_set to prevent Mock from auto-creating subscription attribute
        delattr(mock_request.state, "subscription") if hasattr(mock_request.state, "subscription") else None

        check_plan = require_subscription_plan("premium")

        with pytest.raises(HTTPException) as exc_info:
            await check_plan(mock_request)

        assert exc_info.value.status_code == 500
        assert "not available" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_free_plan_requirement_succeeds(self):
        """Test that any user can access free endpoints"""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.subscription = {
            "plan": "free",
            "is_premium": False,
        }

        check_plan = require_subscription_plan("free")
        # Should not raise
        await check_plan(mock_request)


class TestGetSubscriptionFromRequest:
    """Test get_subscription_from_request helper function"""

    def test_get_subscription_with_subscription_present(self):
        """Test getting subscription info when present"""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.subscription = {
            "plan": "premium",
            "status": "active",
            "is_premium": True,
            "entitlement_active": True,
        }

        subscription = get_subscription_from_request(mock_request)

        assert subscription["plan"] == "premium"
        assert subscription["is_premium"] is True

    def test_get_subscription_without_subscription_returns_default(self):
        """Test getting subscription returns default when not present"""
        mock_request = Mock(spec=Request)

        # Create a mock state without subscription attribute
        class MockState:
            pass

        mock_request.state = MockState()

        subscription = get_subscription_from_request(mock_request)

        assert subscription["plan"] == "free"
        assert subscription["status"] == "inactive"
        assert subscription["is_premium"] is False
        assert subscription["entitlement_active"] is False

    def test_get_subscription_with_none_returns_default(self):
        """Test getting subscription returns default when None"""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.subscription = None

        subscription = get_subscription_from_request(mock_request)

        assert subscription["plan"] == "free"
        assert subscription["is_premium"] is False


class TestSubscriptionMiddlewareIntegration:
    """Test integration scenarios for subscription middleware"""

    @pytest.mark.asyncio
    async def test_subscription_info_persists_through_request(self):
        """Test that subscription info is available throughout request lifecycle"""
        user_id = uuid4()
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.user = {"id": str(user_id)}

        mock_call_next = AsyncMock(return_value=Mock())

        mock_session = AsyncMock()
        mock_subscription_info = MockSubscriptionInfo(
            plan_type="premium", is_active=True
        )

        async def mock_get_db_session():
            yield mock_session

        mock_subscription_service = AsyncMock()
        mock_subscription_service.get_or_create_subscription_info.return_value = (
            mock_subscription_info
        )

        with patch(
            "app.shared.presentation.middleware.subscription_check.get_db_session",
            return_value=mock_get_db_session(),
        ), patch(
            "app.shared.presentation.middleware.subscription_check.get_subscription_service",
            return_value=mock_subscription_service,
        ):
            await check_subscription_permission(mock_request, mock_call_next)

            # Verify subscription can be retrieved after middleware
            subscription = get_subscription_from_request(mock_request)
            assert subscription["is_premium"] is True

    @pytest.mark.asyncio
    async def test_different_subscription_types_handled_correctly(self):
        """Test that different subscription types are handled correctly"""
        test_cases = [
            ("free", True, False),
            ("premium", True, True),
            ("free", False, False),
            ("premium", False, False),
        ]

        for plan_type, is_active, expected_premium in test_cases:
            user_id = uuid4()
            mock_request = Mock(spec=Request)
            mock_request.state = Mock()
            mock_request.state.user = {"id": str(user_id)}

            mock_call_next = AsyncMock(return_value=Mock())

            mock_session = AsyncMock()
            mock_subscription_info = MockSubscriptionInfo(
                plan_type=plan_type, is_active=is_active
            )

            async def mock_get_db_session():
                yield mock_session

            mock_subscription_service = AsyncMock()
            mock_subscription_service.get_or_create_subscription_info.return_value = (
                mock_subscription_info
            )

            with patch(
                "app.shared.presentation.middleware.subscription_check.get_db_session",
                return_value=mock_get_db_session(),
            ), patch(
                "app.shared.presentation.middleware.subscription_check.get_subscription_service",
                return_value=mock_subscription_service,
            ):
                await check_subscription_permission(mock_request, mock_call_next)

                assert (
                    mock_request.state.subscription["is_premium"] == expected_premium
                )
