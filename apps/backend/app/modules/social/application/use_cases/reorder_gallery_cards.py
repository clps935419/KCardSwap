"""
Use case for reordering gallery cards.
"""
from typing import List
from uuid import UUID

from app.modules.social.domain.entities.gallery_card import GalleryCard
from app.modules.social.domain.repositories.i_gallery_card_repository import (
    IGalleryCardRepository,
)


class ReorderGalleryCardsUseCase:
    """
    Use case for reordering a user's gallery cards.

    Business rules:
    - User can only reorder their own cards
    - Cards not in the provided list retain their original order relative to each other
    - New order is assigned sequentially starting from 0
    """

    def __init__(self, gallery_card_repository: IGalleryCardRepository):
        self._repository = gallery_card_repository

    async def execute(self, user_id: UUID, card_ids: List[UUID]) -> List[GalleryCard]:
        """
        Reorder gallery cards for a user.

        Args:
            user_id: The user who owns the cards
            card_ids: List of card IDs in the desired order

        Returns:
            List of reordered GalleryCard entities

        Raises:
            ValueError: If card_ids is empty or contains cards not owned by user
        """
        if not card_ids:
            raise ValueError("Card IDs list cannot be empty")

        # Get all user's cards
        all_cards = await self._repository.find_by_user_id(user_id)

        # Verify all provided card IDs belong to the user
        user_card_ids = {card.id for card in all_cards}
        provided_card_ids = set(card_ids)

        invalid_ids = provided_card_ids - user_card_ids
        if invalid_ids:
            raise ValueError(f"Card IDs not owned by user: {invalid_ids}")

        # Build new order mapping
        # Cards in card_ids list get priority order (0, 1, 2, ...)
        # Cards not in the list keep their relative order after
        new_order_map = {}
        next_order = 0

        # First, assign order to cards in the provided list
        for card_id in card_ids:
            new_order_map[card_id] = next_order
            next_order += 1

        # Then, assign order to remaining cards (preserving their relative order)
        remaining_cards = [card for card in all_cards if card.id not in provided_card_ids]
        remaining_cards.sort(key=lambda c: c.display_order)

        for card in remaining_cards:
            new_order_map[card.id] = next_order
            next_order += 1

        # Update all cards with new order
        updated_cards = []
        for card in all_cards:
            new_order = new_order_map[card.id]
            card.update_order(new_order)
            updated_card = await self._repository.update(card)
            updated_cards.append(updated_card)

        # Sort by new order before returning
        updated_cards.sort(key=lambda c: c.display_order)
        return updated_cards
