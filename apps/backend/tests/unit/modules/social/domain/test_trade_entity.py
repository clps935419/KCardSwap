"""
Unit tests for Trade Entity (T162)
Testing trade entity creation, validation, and business logic
"""
from datetime import datetime
from uuid import uuid4

import pytest

from app.modules.social.domain.entities.trade import Trade


class TestTradeCreation:
    """Test trade creation and validation"""

    def test_trade_creation_with_valid_values(self):
        """Test creating trade with valid values"""
        trade_id = uuid4()
        initiator_id = uuid4()
        responder_id = uuid4()
        now = datetime.utcnow()

        trade = Trade(
            id=trade_id,
            initiator_id=initiator_id,
            responder_id=responder_id,
            status=Trade.STATUS_PROPOSED,
            created_at=now,
            updated_at=now,
        )

        assert trade.id == trade_id
        assert trade.initiator_id == initiator_id
        assert trade.responder_id == responder_id
        assert trade.status == Trade.STATUS_PROPOSED
        assert trade.created_at == now

    def test_trade_validation_invalid_status(self):
        """Test validation fails for invalid status"""
        with pytest.raises(ValueError, match="Invalid trade status"):
            Trade(
                id=uuid4(),
                initiator_id=uuid4(),
                responder_id=uuid4(),
                status="invalid_status",
            )

    def test_trade_validation_same_user(self):
        """Test validation fails when initiator and responder are the same"""
        user_id = uuid4()

        with pytest.raises(ValueError, match="must be different users"):
            Trade(
                id=uuid4(),
                initiator_id=user_id,
                responder_id=user_id,
                status=Trade.STATUS_PROPOSED,
            )

    def test_trade_validation_completed_without_timestamp(self):
        """Test validation fails for completed trade without completed_at"""
        with pytest.raises(ValueError, match="must have completed_at"):
            Trade(
                id=uuid4(),
                initiator_id=uuid4(),
                responder_id=uuid4(),
                status=Trade.STATUS_COMPLETED,
                completed_at=None,
            )

    def test_trade_validation_completed_without_confirmations(self):
        """Test validation fails for completed trade without both confirmations"""
        now = datetime.utcnow()

        # Missing responder confirmation
        with pytest.raises(ValueError, match="must have both confirmations"):
            Trade(
                id=uuid4(),
                initiator_id=uuid4(),
                responder_id=uuid4(),
                status=Trade.STATUS_COMPLETED,
                initiator_confirmed_at=now,
                completed_at=now,
            )

        # Missing initiator confirmation
        with pytest.raises(ValueError, match="must have both confirmations"):
            Trade(
                id=uuid4(),
                initiator_id=uuid4(),
                responder_id=uuid4(),
                status=Trade.STATUS_COMPLETED,
                responder_confirmed_at=now,
                completed_at=now,
            )


class TestTradeStatusChecks:
    """Test trade status checking methods"""

    def test_can_accept_proposed(self):
        """Test can_accept returns True for proposed trade"""
        trade = Trade(
            id=uuid4(),
            initiator_id=uuid4(),
            responder_id=uuid4(),
            status=Trade.STATUS_PROPOSED,
        )

        assert trade.can_accept() is True

    def test_can_accept_not_proposed(self):
        """Test can_accept returns False for non-proposed status"""
        trade = Trade(
            id=uuid4(),
            initiator_id=uuid4(),
            responder_id=uuid4(),
            status=Trade.STATUS_ACCEPTED,
        )

        assert trade.can_accept() is False

    def test_can_reject_proposed_or_draft(self):
        """Test can_reject returns True for proposed or draft"""
        proposed_trade = Trade(
            id=uuid4(),
            initiator_id=uuid4(),
            responder_id=uuid4(),
            status=Trade.STATUS_PROPOSED,
        )

        draft_trade = Trade(
            id=uuid4(),
            initiator_id=uuid4(),
            responder_id=uuid4(),
            status=Trade.STATUS_DRAFT,
        )

        assert proposed_trade.can_reject() is True
        assert draft_trade.can_reject() is True

    def test_can_cancel_active_statuses(self):
        """Test can_cancel returns True for draft, proposed, accepted"""
        for status in [Trade.STATUS_DRAFT, Trade.STATUS_PROPOSED, Trade.STATUS_ACCEPTED]:
            trade = Trade(
                id=uuid4(),
                initiator_id=uuid4(),
                responder_id=uuid4(),
                status=status,
            )
            assert trade.can_cancel() is True

    def test_can_confirm_accepted(self):
        """Test can_confirm returns True for accepted trade"""
        trade = Trade(
            id=uuid4(),
            initiator_id=uuid4(),
            responder_id=uuid4(),
            status=Trade.STATUS_ACCEPTED,
            accepted_at=datetime.utcnow(),
        )

        assert trade.can_confirm() is True

    def test_is_completed_both_confirmed(self):
        """Test is_completed returns True when both parties confirmed"""
        now = datetime.utcnow()
        trade = Trade(
            id=uuid4(),
            initiator_id=uuid4(),
            responder_id=uuid4(),
            status=Trade.STATUS_ACCEPTED,
            initiator_confirmed_at=now,
            responder_confirmed_at=now,
        )

        assert trade.is_completed() is True

    def test_is_completed_partial_confirmation(self):
        """Test is_completed returns False with partial confirmation"""
        now = datetime.utcnow()

        trade = Trade(
            id=uuid4(),
            initiator_id=uuid4(),
            responder_id=uuid4(),
            status=Trade.STATUS_ACCEPTED,
            initiator_confirmed_at=now,
        )

        assert trade.is_completed() is False


class TestTradeStateQueries:
    """Test trade state query methods"""

    def test_is_active(self):
        """Test is_active returns True for draft, proposed, accepted"""
        for status in [Trade.STATUS_DRAFT, Trade.STATUS_PROPOSED, Trade.STATUS_ACCEPTED]:
            trade = Trade(
                id=uuid4(),
                initiator_id=uuid4(),
                responder_id=uuid4(),
                status=status,
            )
            assert trade.is_active() is True

    def test_is_terminal(self):
        """Test is_terminal returns True for completed, rejected, canceled"""
        now = datetime.utcnow()

        for status in [Trade.STATUS_COMPLETED, Trade.STATUS_REJECTED, Trade.STATUS_CANCELED]:
            if status == Trade.STATUS_COMPLETED:
                trade = Trade(
                    id=uuid4(),
                    initiator_id=uuid4(),
                    responder_id=uuid4(),
                    status=status,
                    initiator_confirmed_at=now,
                    responder_confirmed_at=now,
                    completed_at=now,
                )
            else:
                trade = Trade(
                    id=uuid4(),
                    initiator_id=uuid4(),
                    responder_id=uuid4(),
                    status=status,
                )
            assert trade.is_terminal() is True

    def test_has_user(self):
        """Test has_user returns True for participants"""
        initiator_id = uuid4()
        responder_id = uuid4()
        other_id = uuid4()

        trade = Trade(
            id=uuid4(),
            initiator_id=initiator_id,
            responder_id=responder_id,
            status=Trade.STATUS_PROPOSED,
        )

        assert trade.has_user(initiator_id) is True
        assert trade.has_user(responder_id) is True
        assert trade.has_user(other_id) is False

    def test_is_initiator(self):
        """Test is_initiator correctly identifies initiator"""
        initiator_id = uuid4()
        responder_id = uuid4()

        trade = Trade(
            id=uuid4(),
            initiator_id=initiator_id,
            responder_id=responder_id,
            status=Trade.STATUS_PROPOSED,
        )

        assert trade.is_initiator(initiator_id) is True
        assert trade.is_initiator(responder_id) is False

    def test_is_responder(self):
        """Test is_responder correctly identifies responder"""
        initiator_id = uuid4()
        responder_id = uuid4()

        trade = Trade(
            id=uuid4(),
            initiator_id=initiator_id,
            responder_id=responder_id,
            status=Trade.STATUS_PROPOSED,
        )

        assert trade.is_responder(responder_id) is True
        assert trade.is_responder(initiator_id) is False


class TestTradeValidStatuses:
    """Test all valid trade statuses"""

    def test_all_valid_statuses(self):
        """Test that all defined statuses are valid"""
        valid_statuses = [
            Trade.STATUS_DRAFT,
            Trade.STATUS_PROPOSED,
            Trade.STATUS_ACCEPTED,
            Trade.STATUS_COMPLETED,
            Trade.STATUS_REJECTED,
            Trade.STATUS_CANCELED,
        ]

        for status in valid_statuses:
            assert status in Trade.VALID_STATUSES

    def test_status_constants_match(self):
        """Test status constants have expected values"""
        assert Trade.STATUS_DRAFT == "draft"
        assert Trade.STATUS_PROPOSED == "proposed"
        assert Trade.STATUS_ACCEPTED == "accepted"
        assert Trade.STATUS_COMPLETED == "completed"
        assert Trade.STATUS_REJECTED == "rejected"
        assert Trade.STATUS_CANCELED == "canceled"
