"""
Get My Cards Use Case - Retrieve user's card collection
"""

from typing import List
from uuid import UUID

from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.repositories.i_card_repository import ICardRepository


class GetMyCardsUseCase:
    """Use case for retrieving user's cards"""

    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    async def execute(self, owner_id: UUID, status: str = None) -> List[Card]:
        """
        Get all cards owned by a user.

        Args:
            owner_id: Owner's user ID
            status: Optional status filter (available/trading/traded)

        Returns:
            List of cards (empty if none found)
        """
        if status:
            # Filter by status
            return await self.card_repository.find_by_status(owner_id, status)
        else:
            # Get all cards
            return await self.card_repository.find_by_owner(owner_id)
