"""
Unit tests for TradeValidationService

Tests the trade validation domain service.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.entities.trade_item import TradeItem
from app.modules.social.domain.services.trade_validation_service import (
    TradeValidationService,
)
from app.modules.social.domain.value_objects.trade_status import TradeStatus


class TestTradeValidationService:
    """Test TradeValidationService"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return TradeValidationService()

    @pytest.fixture
    def sample_card(self):
        """Create sample available card"""
        return Card(
            id=uuid4(),
            owner_id=uuid4(),
            idol_name="IU",
            idol_group="Solo",
            card_name="Love Poem",
            image_url="https://example.com/image.jpg",
            status="available",
            latitude=25.033,
            longitude=121.564,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_trade(self):
        """Create sample pending trade"""
        initiator_id = uuid4()
        responder_id = uuid4()
        return Trade(
            id=str(uuid4()),
            initiator_id=initiator_id,
            responder_id=responder_id,
            status=TradeStatus.PENDING.value,
            created_at=datetime.now(timezone.utc),
        )

    def test_validate_card_ownership_success(self, service, sample_card):
        """Test successful card ownership validation"""
        # Should not raise exception
        service.validate_card_ownership(
            cards=[sample_card],
            user_id=sample_card.owner_id,
            expected_side="initiator",
        )

    def test_validate_card_ownership_failure(self, service, sample_card):
        """Test card ownership validation fails for wrong owner"""
        wrong_user_id = uuid4()
        with pytest.raises(ValueError, match="is not owned by user"):
            service.validate_card_ownership(
                cards=[sample_card],
                user_id=wrong_user_id,
                expected_side="initiator",
            )

    def test_validate_card_ownership_multiple_cards(self, service):
        """Test validating ownership of multiple cards"""
        owner_id = uuid4()
        cards = [
            Card(
                id=uuid4(),
                owner_id=owner_id,
                idol_name=f"Idol {i}",
                idol_group="Group",
                card_name=f"Card {i}",
                image_url=f"https://example.com/image{i}.jpg",
                status="available",
                latitude=25.033,
                longitude=121.564,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            for i in range(3)
        ]

        # Should not raise exception
        service.validate_card_ownership(
            cards=cards,
            user_id=owner_id,
            expected_side="initiator",
        )

    def test_validate_card_availability_success(self, service, sample_card):
        """Test successful card availability validation"""
        # Should not raise exception
        service.validate_card_availability([sample_card])

    def test_validate_card_availability_failure(self, service, sample_card):
        """Test card availability validation fails for unavailable card"""
        sample_card.status = "traded"
        with pytest.raises(ValueError, match="is not available for trading"):
            service.validate_card_availability([sample_card])

    def test_validate_status_transition_valid(self, service):
        """Test valid status transitions"""
        # Pending -> Accepted
        service.validate_status_transition(
            TradeStatus.PENDING.value,
            TradeStatus.ACCEPTED.value,
        )

        # Pending -> Rejected
        service.validate_status_transition(
            TradeStatus.PENDING.value,
            TradeStatus.REJECTED.value,
        )

        # Accepted -> Completed
        service.validate_status_transition(
            TradeStatus.ACCEPTED.value,
            TradeStatus.COMPLETED.value,
        )

    def test_validate_status_transition_invalid(self, service):
        """Test invalid status transitions are rejected"""
        # Cannot go from Rejected to Accepted
        with pytest.raises(ValueError, match="Cannot transition"):
            service.validate_status_transition(
                TradeStatus.REJECTED.value,
                TradeStatus.ACCEPTED.value,
            )

        # Cannot go from Completed to Pending
        with pytest.raises(ValueError, match="Cannot transition"):
            service.validate_status_transition(
                TradeStatus.COMPLETED.value,
                TradeStatus.PENDING.value,
            )

    def test_validate_trade_items_success(self, service):
        """Test successful trade items validation"""
        initiator_id = uuid4()
        responder_id = uuid4()
        items = [
            TradeItem(
                id=str(uuid4()),
                trade_id=str(uuid4()),
                card_id=uuid4(),
                owner_side=TradeItem.SIDE_INITIATOR,
            ),
            TradeItem(
                id=str(uuid4()),
                trade_id=str(uuid4()),
                card_id=uuid4(),
                owner_side=TradeItem.SIDE_RESPONDER,
            ),
        ]

        # Should not raise exception
        service.validate_trade_items(items, initiator_id, responder_id)

    def test_validate_trade_items_empty(self, service):
        """Test validation fails for empty trade items"""
        with pytest.raises(ValueError, match="at least one item"):
            service.validate_trade_items([], uuid4(), uuid4())

    def test_validate_trade_items_duplicate_cards(self, service):
        """Test validation fails for duplicate cards"""
        card_id = uuid4()
        items = [
            TradeItem(
                id=str(uuid4()),
                trade_id=str(uuid4()),
                card_id=card_id,
                owner_side=TradeItem.SIDE_INITIATOR,
            ),
            TradeItem(
                id=str(uuid4()),
                trade_id=str(uuid4()),
                card_id=card_id,  # Duplicate
                owner_side=TradeItem.SIDE_INITIATOR,
            ),
        ]

        with pytest.raises(ValueError, match="duplicate cards"):
            service.validate_trade_items(items, uuid4(), uuid4())

    def test_validate_trade_items_invalid_owner_side(self, service):
        """Test validation fails for invalid owner_side"""
        items = [
            TradeItem(
                id=str(uuid4()),
                trade_id=str(uuid4()),
                card_id=uuid4(),
                owner_side="invalid_side",
            ),
        ]

        with pytest.raises(ValueError, match="Invalid owner_side"):
            service.validate_trade_items(items, uuid4(), uuid4())

    def test_validate_user_can_accept_success(self, service, sample_trade):
        """Test successful validation for accepting trade"""
        # Should not raise exception
        service.validate_user_can_accept(sample_trade, sample_trade.responder_id)

    def test_validate_user_can_accept_wrong_user(self, service, sample_trade):
        """Test validation fails when non-responder tries to accept"""
        with pytest.raises(ValueError, match="Only responder can accept"):
            service.validate_user_can_accept(sample_trade, sample_trade.initiator_id)

    def test_validate_user_can_accept_wrong_status(self, service, sample_trade):
        """Test validation fails for wrong trade status"""
        sample_trade.status = TradeStatus.COMPLETED.value
        with pytest.raises(ValueError, match="cannot be accepted"):
            service.validate_user_can_accept(sample_trade, sample_trade.responder_id)

    def test_validate_user_can_reject_success(self, service, sample_trade):
        """Test successful validation for rejecting trade"""
        # Should not raise exception
        service.validate_user_can_reject(sample_trade, sample_trade.responder_id)

    def test_validate_user_can_reject_wrong_user(self, service, sample_trade):
        """Test validation fails when non-responder tries to reject"""
        with pytest.raises(ValueError, match="Only responder can reject"):
            service.validate_user_can_reject(sample_trade, sample_trade.initiator_id)

    def test_validate_user_can_reject_wrong_status(self, service, sample_trade):
        """Test validation fails for wrong trade status"""
        sample_trade.status = TradeStatus.COMPLETED.value
        with pytest.raises(ValueError, match="cannot be rejected"):
            service.validate_user_can_reject(sample_trade, sample_trade.responder_id)

    def test_validate_user_can_cancel_success(self, service, sample_trade):
        """Test successful validation for canceling trade"""
        # Both initiator and responder should be able to cancel
        service.validate_user_can_cancel(sample_trade, sample_trade.initiator_id)
        service.validate_user_can_cancel(sample_trade, sample_trade.responder_id)

    def test_validate_user_can_cancel_wrong_user(self, service, sample_trade):
        """Test validation fails when non-participant tries to cancel"""
        with pytest.raises(ValueError, match="Only trade participants can cancel"):
            service.validate_user_can_cancel(sample_trade, uuid4())

    def test_validate_user_can_cancel_wrong_status(self, service, sample_trade):
        """Test validation fails for wrong trade status"""
        sample_trade.status = TradeStatus.COMPLETED.value
        with pytest.raises(ValueError, match="cannot be canceled"):
            service.validate_user_can_cancel(sample_trade, sample_trade.initiator_id)

    def test_validate_user_can_confirm_success(self, service, sample_trade):
        """Test successful validation for confirming trade"""
        sample_trade.status = TradeStatus.ACCEPTED.value
        # Both participants should be able to confirm
        service.validate_user_can_confirm(sample_trade, sample_trade.initiator_id)
        service.validate_user_can_confirm(sample_trade, sample_trade.responder_id)

    def test_validate_user_can_confirm_wrong_user(self, service, sample_trade):
        """Test validation fails when non-participant tries to confirm"""
        sample_trade.status = TradeStatus.ACCEPTED.value
        with pytest.raises(ValueError, match="Only trade participants can confirm"):
            service.validate_user_can_confirm(sample_trade, uuid4())

    def test_validate_user_can_confirm_wrong_status(self, service, sample_trade):
        """Test validation fails for wrong trade status"""
        sample_trade.status = TradeStatus.PENDING.value
        with pytest.raises(ValueError, match="cannot be confirmed"):
            service.validate_user_can_confirm(sample_trade, sample_trade.initiator_id)
