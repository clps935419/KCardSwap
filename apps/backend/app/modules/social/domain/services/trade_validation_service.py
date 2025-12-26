"""Trade Validation Service - Domain service for trade business rules."""

from typing import List
from uuid import UUID

from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.entities.trade import Trade
from app.modules.social.domain.entities.trade_item import TradeItem
from app.modules.social.domain.value_objects.trade_status import TradeStatus


class TradeValidationService:
    """
    Domain service for validating trade business rules.

    Enforces:
    - Card ownership validation
    - Card availability validation
    - Trade status transition rules
    - Trade item constraints
    """

    def validate_card_ownership(
        self,
        cards: List[Card],
        user_id: UUID,
        expected_side: str,
    ) -> None:
        """
        Validate that all cards are owned by the correct user.

        Args:
            cards: List of cards to validate
            user_id: Expected owner user ID
            expected_side: Expected side (initiator/responder)

        Raises:
            ValueError: If any card is not owned by user
        """
        for card in cards:
            if card.owner_id != user_id:
                raise ValueError(
                    f"Card {card.id} is not owned by user {user_id}. "
                    f"Cannot add to {expected_side} side of trade."
                )

    def validate_card_availability(self, cards: List[Card]) -> None:
        """
        Validate that all cards are available for trading.

        Args:
            cards: List of cards to validate

        Raises:
            ValueError: If any card is not available
        """
        for card in cards:
            if card.status != Card.STATUS_AVAILABLE:
                raise ValueError(
                    f"Card {card.id} is not available for trading. "
                    f"Current status: {card.status}"
                )

    def validate_status_transition(
        self,
        current_status: str,
        new_status: str,
    ) -> None:
        """
        Validate trade status transition.

        Args:
            current_status: Current trade status
            new_status: Target status

        Raises:
            ValueError: If transition is not valid
        """
        status = TradeStatus(current_status)
        if not status.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition trade from {current_status} to {new_status}"
            )

    def validate_trade_items(
        self,
        items: List[TradeItem],
        initiator_id: UUID,
        responder_id: UUID,
    ) -> None:
        """
        Validate trade items.

        Args:
            items: List of trade items
            initiator_id: Initiator user ID
            responder_id: Responder user ID

        Raises:
            ValueError: If items are invalid
        """
        if not items:
            raise ValueError("Trade must have at least one item")

        # Check for duplicate cards
        card_ids = [item.card_id for item in items]
        if len(card_ids) != len(set(card_ids)):
            raise ValueError("Trade cannot contain duplicate cards")

        # Validate owner_side values
        for item in items:
            if item.owner_side not in (
                TradeItem.SIDE_INITIATOR,
                TradeItem.SIDE_RESPONDER,
            ):
                raise ValueError(f"Invalid owner_side: {item.owner_side}")

    def validate_user_can_accept(self, trade: Trade, user_id: UUID) -> None:
        """
        Validate that user can accept trade.

        Args:
            trade: Trade to validate
            user_id: User attempting to accept

        Raises:
            ValueError: If user cannot accept
        """
        if not trade.can_accept():
            raise ValueError(
                f"Trade cannot be accepted. Current status: {trade.status}"
            )

        if not trade.is_responder(user_id):
            raise ValueError("Only responder can accept trade")

    def validate_user_can_reject(self, trade: Trade, user_id: UUID) -> None:
        """
        Validate that user can reject trade.

        Args:
            trade: Trade to validate
            user_id: User attempting to reject

        Raises:
            ValueError: If user cannot reject
        """
        if not trade.can_reject():
            raise ValueError(
                f"Trade cannot be rejected. Current status: {trade.status}"
            )

        if not trade.is_responder(user_id):
            raise ValueError("Only responder can reject trade")

    def validate_user_can_cancel(self, trade: Trade, user_id: UUID) -> None:
        """
        Validate that user can cancel trade.

        Args:
            trade: Trade to validate
            user_id: User attempting to cancel

        Raises:
            ValueError: If user cannot cancel
        """
        if not trade.can_cancel():
            raise ValueError(
                f"Trade cannot be canceled. Current status: {trade.status}"
            )

        if not trade.has_user(user_id):
            raise ValueError("Only trade participants can cancel trade")

    def validate_user_can_confirm(self, trade: Trade, user_id: UUID) -> None:
        """
        Validate that user can confirm completion.

        Args:
            trade: Trade to validate
            user_id: User attempting to confirm

        Raises:
            ValueError: If user cannot confirm
        """
        if not trade.can_confirm():
            raise ValueError(
                f"Trade cannot be confirmed. Current status: {trade.status}"
            )

        if not trade.has_user(user_id):
            raise ValueError("Only trade participants can confirm trade")
