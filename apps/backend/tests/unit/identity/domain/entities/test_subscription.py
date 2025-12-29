"""
Unit tests for Subscription Entity
Testing subscription management and status transitions
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.modules.identity.domain.entities.subscription import Subscription


class TestSubscriptionCreation:
    """Test subscription entity creation and initialization"""

    def test_create_free_subscription(self):
        """Test creating a free subscription"""
        user_id = uuid4()

        subscription = Subscription(
            id=None,
            user_id=user_id,
            plan="free",
            status="inactive",
            expires_at=None,
        )

        assert subscription.user_id == user_id
        assert subscription.plan == "free"
        assert subscription.status == "inactive"
        assert subscription.expires_at is None
        assert isinstance(subscription.created_at, datetime)
        assert isinstance(subscription.updated_at, datetime)

    def test_create_premium_subscription(self):
        """Test creating a premium subscription"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        assert subscription.id == 1
        assert subscription.user_id == user_id
        assert subscription.plan == "premium"
        assert subscription.status == "active"
        assert subscription.expires_at == expires_at

    def test_create_subscription_with_timestamps(self):
        """Test creating a subscription with specific timestamps"""
        user_id = uuid4()
        now = datetime.utcnow()
        expires_at = now + timedelta(days=30)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
            created_at=now,
            updated_at=now,
        )

        assert subscription.created_at == now
        assert subscription.updated_at == now

    def test_create_pending_subscription(self):
        """Test creating a pending subscription"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=None,
            user_id=user_id,
            plan="premium",
            status="pending",
            expires_at=expires_at,
        )

        assert subscription.status == "pending"

    def test_create_expired_subscription(self):
        """Test creating an expired subscription"""
        user_id = uuid4()
        expires_at = datetime.utcnow() - timedelta(days=1)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="expired",
            expires_at=expires_at,
        )

        assert subscription.status == "expired"


class TestSubscriptionStatusChecks:
    """Test subscription status checking methods"""

    def test_is_active_for_active_subscription(self):
        """Test is_active returns True for active subscription with future expiry"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        assert subscription.is_active() is True

    def test_is_active_for_inactive_subscription(self):
        """Test is_active returns False for inactive subscription"""
        user_id = uuid4()

        subscription = Subscription(
            id=None,
            user_id=user_id,
            plan="free",
            status="inactive",
            expires_at=None,
        )

        assert subscription.is_active() is False

    def test_is_active_for_expired_status(self):
        """Test is_active returns False for expired status"""
        user_id = uuid4()
        expires_at = datetime.utcnow() - timedelta(days=1)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="expired",
            expires_at=expires_at,
        )

        assert subscription.is_active() is False

    def test_is_active_for_pending_status(self):
        """Test is_active returns False for pending status"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=None,
            user_id=user_id,
            plan="premium",
            status="pending",
            expires_at=expires_at,
        )

        assert subscription.is_active() is False

    def test_is_active_when_expires_at_is_none(self):
        """Test is_active returns False when expires_at is None"""
        user_id = uuid4()

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=None,
        )

        assert subscription.is_active() is False

    def test_is_active_when_expired(self):
        """Test is_active returns False when expiration date has passed"""
        user_id = uuid4()
        expires_at = datetime.utcnow() - timedelta(seconds=1)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        assert subscription.is_active() is False

    def test_is_premium_for_active_premium(self):
        """Test is_premium returns True for active premium subscription"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        assert subscription.is_premium() is True

    def test_is_premium_for_free_plan(self):
        """Test is_premium returns False for free plan"""
        user_id = uuid4()

        subscription = Subscription(
            id=None,
            user_id=user_id,
            plan="free",
            status="inactive",
            expires_at=None,
        )

        assert subscription.is_premium() is False

    def test_is_premium_for_expired_premium(self):
        """Test is_premium returns False for expired premium"""
        user_id = uuid4()
        expires_at = datetime.utcnow() - timedelta(days=1)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="expired",
            expires_at=expires_at,
        )

        assert subscription.is_premium() is False

    def test_is_premium_for_inactive_premium(self):
        """Test is_premium returns False for inactive premium"""
        user_id = uuid4()

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="inactive",
            expires_at=None,
        )

        assert subscription.is_premium() is False


class TestSubscriptionExpirationChecks:
    """Test subscription expiration checking methods"""

    def test_should_expire_for_past_expiration(self):
        """Test should_expire returns True when expiration date has passed"""
        user_id = uuid4()
        expires_at = datetime.utcnow() - timedelta(seconds=1)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        assert subscription.should_expire() is True

    def test_should_expire_for_future_expiration(self):
        """Test should_expire returns False for future expiration"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        assert subscription.should_expire() is False

    def test_should_expire_for_inactive_status(self):
        """Test should_expire returns False for inactive status"""
        user_id = uuid4()

        subscription = Subscription(
            id=None,
            user_id=user_id,
            plan="free",
            status="inactive",
            expires_at=None,
        )

        assert subscription.should_expire() is False

    def test_should_expire_for_expired_status(self):
        """Test should_expire returns False for already expired status"""
        user_id = uuid4()
        expires_at = datetime.utcnow() - timedelta(days=1)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="expired",
            expires_at=expires_at,
        )

        assert subscription.should_expire() is False

    def test_should_expire_when_expires_at_is_none(self):
        """Test should_expire returns False when expires_at is None"""
        user_id = uuid4()

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=None,
        )

        assert subscription.should_expire() is False


class TestSubscriptionStateTransitions:
    """Test subscription state transition methods"""

    def test_mark_as_expired(self):
        """Test marking a subscription as expired"""
        user_id = uuid4()
        expires_at = datetime.utcnow() - timedelta(days=1)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        old_updated_at = subscription.updated_at
        subscription.mark_as_expired()

        assert subscription.status == "expired"
        assert subscription.updated_at > old_updated_at

    def test_activate_premium_subscription(self):
        """Test activating a premium subscription"""
        user_id = uuid4()
        new_expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="free",
            status="inactive",
            expires_at=None,
        )

        old_updated_at = subscription.updated_at
        subscription.activate(new_expires_at)

        assert subscription.plan == "premium"
        assert subscription.status == "active"
        assert subscription.expires_at == new_expires_at
        assert subscription.updated_at > old_updated_at

    def test_activate_updates_existing_premium(self):
        """Test activating/renewing an existing premium subscription"""
        user_id = uuid4()
        old_expires_at = datetime.utcnow() + timedelta(days=5)
        new_expires_at = datetime.utcnow() + timedelta(days=35)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=old_expires_at,
        )

        subscription.activate(new_expires_at)

        assert subscription.plan == "premium"
        assert subscription.status == "active"
        assert subscription.expires_at == new_expires_at

    def test_deactivate_subscription(self):
        """Test deactivating a subscription"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        old_updated_at = subscription.updated_at
        subscription.deactivate()

        assert subscription.plan == "free"
        assert subscription.status == "inactive"
        assert subscription.expires_at is None
        assert subscription.updated_at > old_updated_at

    def test_deactivate_already_free_subscription(self):
        """Test deactivating an already free subscription"""
        user_id = uuid4()

        subscription = Subscription(
            id=None,
            user_id=user_id,
            plan="free",
            status="inactive",
            expires_at=None,
        )

        subscription.deactivate()

        assert subscription.plan == "free"
        assert subscription.status == "inactive"
        assert subscription.expires_at is None


class TestSubscriptionRepresentation:
    """Test subscription string representation"""

    def test_repr(self):
        """Test subscription __repr__ method"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=expires_at,
        )

        repr_str = repr(subscription)
        assert "Subscription" in repr_str
        assert "id=1" in repr_str
        assert f"user_id={user_id}" in repr_str
        assert "plan=premium" in repr_str
        assert "status=active" in repr_str

    def test_repr_with_none_id(self):
        """Test subscription __repr__ with None id"""
        user_id = uuid4()

        subscription = Subscription(
            id=None,
            user_id=user_id,
            plan="free",
            status="inactive",
            expires_at=None,
        )

        repr_str = repr(subscription)
        assert "Subscription" in repr_str
        assert "id=None" in repr_str


class TestSubscriptionLifecycle:
    """Test complete subscription lifecycle scenarios"""

    def test_full_premium_lifecycle(self):
        """Test complete lifecycle: free -> premium -> expired -> free"""
        user_id = uuid4()

        # Start with free subscription
        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="free",
            status="inactive",
            expires_at=None,
        )

        assert subscription.is_premium() is False
        assert subscription.is_active() is False

        # Upgrade to premium
        expires_at = datetime.utcnow() + timedelta(days=30)
        subscription.activate(expires_at)

        assert subscription.is_premium() is True
        assert subscription.is_active() is True
        assert subscription.plan == "premium"
        assert subscription.status == "active"

        # Mark as expired
        subscription.mark_as_expired()

        assert subscription.is_premium() is False
        assert subscription.is_active() is False
        assert subscription.status == "expired"

        # Deactivate (return to free)
        subscription.deactivate()

        assert subscription.plan == "free"
        assert subscription.status == "inactive"
        assert subscription.expires_at is None

    def test_renewal_scenario(self):
        """Test renewing an active premium subscription"""
        user_id = uuid4()
        first_expires = datetime.utcnow() + timedelta(days=5)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="active",
            expires_at=first_expires,
        )

        assert subscription.is_premium() is True

        # Renew before expiration
        new_expires = datetime.utcnow() + timedelta(days=35)
        subscription.activate(new_expires)

        assert subscription.is_premium() is True
        assert subscription.expires_at == new_expires

    def test_reactivation_after_expiry(self):
        """Test reactivating after subscription expires"""
        user_id = uuid4()
        old_expires = datetime.utcnow() - timedelta(days=1)

        subscription = Subscription(
            id=1,
            user_id=user_id,
            plan="premium",
            status="expired",
            expires_at=old_expires,
        )

        assert subscription.is_premium() is False

        # Reactivate with new expiration
        new_expires = datetime.utcnow() + timedelta(days=30)
        subscription.activate(new_expires)

        assert subscription.is_premium() is True
        assert subscription.status == "active"
        assert subscription.expires_at == new_expires
