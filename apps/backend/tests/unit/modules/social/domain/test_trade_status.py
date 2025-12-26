"""
Unit tests for TradeStatus Value Object (T163)
Testing trade status state machine and transition logic
"""
import pytest

from app.modules.social.domain.value_objects.trade_status import TradeStatus


class TestTradeStatusCreation:
    """Test trade status creation and validation"""

    def test_status_creation_with_valid_value(self):
        """Test creating status with valid value"""
        status = TradeStatus(TradeStatus.PROPOSED)

        assert status.value == TradeStatus.PROPOSED
        assert str(status) == "proposed"

    def test_status_creation_with_invalid_value(self):
        """Test validation fails for invalid status"""
        with pytest.raises(ValueError, match="Invalid trade status"):
            TradeStatus("invalid_status")

    def test_status_is_immutable(self):
        """Test that status is immutable (frozen dataclass)"""
        status = TradeStatus(TradeStatus.PROPOSED)

        with pytest.raises(Exception):  # FrozenInstanceError
            status.value = TradeStatus.ACCEPTED


class TestTradeStatusTransitions:
    """Test trade status transition validation"""

    def test_draft_to_proposed(self):
        """Test transition from draft to proposed"""
        status = TradeStatus(TradeStatus.DRAFT)

        assert status.can_transition_to(TradeStatus.PROPOSED) is True

    def test_draft_to_canceled(self):
        """Test transition from draft to canceled"""
        status = TradeStatus(TradeStatus.DRAFT)

        assert status.can_transition_to(TradeStatus.CANCELED) is True

    def test_draft_invalid_transitions(self):
        """Test invalid transitions from draft"""
        status = TradeStatus(TradeStatus.DRAFT)

        assert status.can_transition_to(TradeStatus.ACCEPTED) is False
        assert status.can_transition_to(TradeStatus.COMPLETED) is False
        assert status.can_transition_to(TradeStatus.REJECTED) is False

    def test_proposed_to_accepted(self):
        """Test transition from proposed to accepted"""
        status = TradeStatus(TradeStatus.PROPOSED)

        assert status.can_transition_to(TradeStatus.ACCEPTED) is True

    def test_proposed_to_rejected(self):
        """Test transition from proposed to rejected"""
        status = TradeStatus(TradeStatus.PROPOSED)

        assert status.can_transition_to(TradeStatus.REJECTED) is True

    def test_proposed_to_canceled(self):
        """Test transition from proposed to canceled"""
        status = TradeStatus(TradeStatus.PROPOSED)

        assert status.can_transition_to(TradeStatus.CANCELED) is True

    def test_proposed_invalid_transitions(self):
        """Test invalid transitions from proposed"""
        status = TradeStatus(TradeStatus.PROPOSED)

        assert status.can_transition_to(TradeStatus.DRAFT) is False
        assert status.can_transition_to(TradeStatus.COMPLETED) is False

    def test_accepted_to_completed(self):
        """Test transition from accepted to completed"""
        status = TradeStatus(TradeStatus.ACCEPTED)

        assert status.can_transition_to(TradeStatus.COMPLETED) is True

    def test_accepted_to_canceled(self):
        """Test transition from accepted to canceled"""
        status = TradeStatus(TradeStatus.ACCEPTED)

        assert status.can_transition_to(TradeStatus.CANCELED) is True

    def test_accepted_invalid_transitions(self):
        """Test invalid transitions from accepted"""
        status = TradeStatus(TradeStatus.ACCEPTED)

        assert status.can_transition_to(TradeStatus.DRAFT) is False
        assert status.can_transition_to(TradeStatus.PROPOSED) is False
        assert status.can_transition_to(TradeStatus.REJECTED) is False

    def test_terminal_states_no_transitions(self):
        """Test terminal states cannot transition"""
        for terminal_status in [
            TradeStatus.COMPLETED,
            TradeStatus.REJECTED,
            TradeStatus.CANCELED,
        ]:
            status = TradeStatus(terminal_status)

            # Cannot transition to any state
            for target in TradeStatus.VALID_STATUSES:
                assert status.can_transition_to(target) is False


class TestTradeStatusStateQueries:
    """Test status state query methods"""

    def test_is_terminal(self):
        """Test is_terminal returns True for terminal statuses"""
        for status_value in [
            TradeStatus.COMPLETED,
            TradeStatus.REJECTED,
            TradeStatus.CANCELED,
        ]:
            status = TradeStatus(status_value)
            assert status.is_terminal() is True

    def test_is_not_terminal(self):
        """Test is_terminal returns False for active statuses"""
        for status_value in [
            TradeStatus.DRAFT,
            TradeStatus.PROPOSED,
            TradeStatus.ACCEPTED,
        ]:
            status = TradeStatus(status_value)
            assert status.is_terminal() is False

    def test_is_active(self):
        """Test is_active returns True for active statuses"""
        for status_value in [
            TradeStatus.DRAFT,
            TradeStatus.PROPOSED,
            TradeStatus.ACCEPTED,
        ]:
            status = TradeStatus(status_value)
            assert status.is_active() is True

    def test_is_not_active(self):
        """Test is_active returns False for terminal statuses"""
        for status_value in [
            TradeStatus.COMPLETED,
            TradeStatus.REJECTED,
            TradeStatus.CANCELED,
        ]:
            status = TradeStatus(status_value)
            assert status.is_active() is False

    def test_is_draft(self):
        """Test is_draft query"""
        assert TradeStatus(TradeStatus.DRAFT).is_draft() is True
        assert TradeStatus(TradeStatus.PROPOSED).is_draft() is False

    def test_is_proposed(self):
        """Test is_proposed query"""
        assert TradeStatus(TradeStatus.PROPOSED).is_proposed() is True
        assert TradeStatus(TradeStatus.DRAFT).is_proposed() is False

    def test_is_accepted(self):
        """Test is_accepted query"""
        assert TradeStatus(TradeStatus.ACCEPTED).is_accepted() is True
        assert TradeStatus(TradeStatus.PROPOSED).is_accepted() is False

    def test_is_completed(self):
        """Test is_completed query"""
        assert TradeStatus(TradeStatus.COMPLETED).is_completed() is True
        assert TradeStatus(TradeStatus.ACCEPTED).is_completed() is False

    def test_is_rejected(self):
        """Test is_rejected query"""
        assert TradeStatus(TradeStatus.REJECTED).is_rejected() is True
        assert TradeStatus(TradeStatus.PROPOSED).is_rejected() is False

    def test_is_canceled(self):
        """Test is_canceled query"""
        assert TradeStatus(TradeStatus.CANCELED).is_canceled() is True
        assert TradeStatus(TradeStatus.ACCEPTED).is_canceled() is False


class TestTradeStatusEquality:
    """Test status equality comparison"""

    def test_status_equality_with_status(self):
        """Test equality comparison with another TradeStatus"""
        status1 = TradeStatus(TradeStatus.PROPOSED)
        status2 = TradeStatus(TradeStatus.PROPOSED)
        status3 = TradeStatus(TradeStatus.ACCEPTED)

        assert status1 == status2
        assert status1 != status3

    def test_status_equality_with_string(self):
        """Test equality comparison with string"""
        status = TradeStatus(TradeStatus.PROPOSED)

        assert status == "proposed"
        assert status != "accepted"

    def test_status_hash(self):
        """Test status can be used in sets/dicts"""
        status1 = TradeStatus(TradeStatus.PROPOSED)
        status2 = TradeStatus(TradeStatus.PROPOSED)
        status3 = TradeStatus(TradeStatus.ACCEPTED)

        status_set = {status1, status2, status3}
        assert len(status_set) == 2  # status1 and status2 are equal


class TestTradeStatusConstants:
    """Test status constants"""

    def test_all_status_constants(self):
        """Test all status constants are defined"""
        assert TradeStatus.DRAFT == "draft"
        assert TradeStatus.PROPOSED == "proposed"
        assert TradeStatus.ACCEPTED == "accepted"
        assert TradeStatus.COMPLETED == "completed"
        assert TradeStatus.REJECTED == "rejected"
        assert TradeStatus.CANCELED == "canceled"

    def test_valid_statuses_set(self):
        """Test VALID_STATUSES contains all statuses"""
        expected_statuses = {
            TradeStatus.DRAFT,
            TradeStatus.PROPOSED,
            TradeStatus.ACCEPTED,
            TradeStatus.COMPLETED,
            TradeStatus.REJECTED,
            TradeStatus.CANCELED,
        }

        assert TradeStatus.VALID_STATUSES == expected_statuses

    def test_terminal_statuses_set(self):
        """Test TERMINAL_STATUSES contains correct statuses"""
        expected_terminal = {
            TradeStatus.COMPLETED,
            TradeStatus.REJECTED,
            TradeStatus.CANCELED,
        }

        assert TradeStatus.TERMINAL_STATUSES == expected_terminal

    def test_active_statuses_set(self):
        """Test ACTIVE_STATUSES contains correct statuses"""
        expected_active = {
            TradeStatus.DRAFT,
            TradeStatus.PROPOSED,
            TradeStatus.ACCEPTED,
        }

        assert TradeStatus.ACTIVE_STATUSES == expected_active


class TestTradeStatusStateMachine:
    """Test complete state machine flow"""

    def test_happy_path_flow(self):
        """Test normal trade flow: draft → proposed → accepted → completed"""
        # Start as draft
        status = TradeStatus(TradeStatus.DRAFT)
        assert status.can_transition_to(TradeStatus.PROPOSED) is True

        # Move to proposed
        status = TradeStatus(TradeStatus.PROPOSED)
        assert status.can_transition_to(TradeStatus.ACCEPTED) is True

        # Move to accepted
        status = TradeStatus(TradeStatus.ACCEPTED)
        assert status.can_transition_to(TradeStatus.COMPLETED) is True

        # Completed (terminal)
        status = TradeStatus(TradeStatus.COMPLETED)
        assert status.is_terminal() is True

    def test_rejection_flow(self):
        """Test rejection flow: proposed → rejected"""
        status = TradeStatus(TradeStatus.PROPOSED)
        assert status.can_transition_to(TradeStatus.REJECTED) is True

        status = TradeStatus(TradeStatus.REJECTED)
        assert status.is_terminal() is True

    def test_cancellation_flow_from_draft(self):
        """Test cancellation from draft"""
        status = TradeStatus(TradeStatus.DRAFT)
        assert status.can_transition_to(TradeStatus.CANCELED) is True

        status = TradeStatus(TradeStatus.CANCELED)
        assert status.is_terminal() is True

    def test_cancellation_flow_from_proposed(self):
        """Test cancellation from proposed"""
        status = TradeStatus(TradeStatus.PROPOSED)
        assert status.can_transition_to(TradeStatus.CANCELED) is True

    def test_cancellation_flow_from_accepted(self):
        """Test cancellation from accepted (e.g., timeout)"""
        status = TradeStatus(TradeStatus.ACCEPTED)
        assert status.can_transition_to(TradeStatus.CANCELED) is True

    def test_invalid_backward_transitions(self):
        """Test backward transitions are not allowed"""
        # Cannot go back from accepted to proposed
        status = TradeStatus(TradeStatus.ACCEPTED)
        assert status.can_transition_to(TradeStatus.PROPOSED) is False

        # Cannot go back from proposed to draft
        status = TradeStatus(TradeStatus.PROPOSED)
        assert status.can_transition_to(TradeStatus.DRAFT) is False

    def test_invalid_skip_transitions(self):
        """Test cannot skip intermediate states"""
        # Cannot go directly from draft to accepted
        status = TradeStatus(TradeStatus.DRAFT)
        assert status.can_transition_to(TradeStatus.ACCEPTED) is False

        # Cannot go directly from draft to completed
        assert status.can_transition_to(TradeStatus.COMPLETED) is False

        # Cannot go directly from proposed to completed
        status = TradeStatus(TradeStatus.PROPOSED)
        assert status.can_transition_to(TradeStatus.COMPLETED) is False
