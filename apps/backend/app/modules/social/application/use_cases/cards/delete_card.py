"""
Delete Card Use Case - Remove a card from collection
"""

from uuid import UUID

from app.modules.social.domain.repositories.card_repository import CardRepository


class DeleteCardUseCase:
    """Use case for deleting a card"""

    def __init__(
        self,
        card_repository: CardRepository,
        gcs_service,  # GCSStorageService or MockGCSStorageService
    ):
        self.card_repository = card_repository
        self.gcs_service = gcs_service

    async def execute(self, card_id: UUID, owner_id: UUID) -> bool:
        """
        Delete a card by ID.
        
        Only the owner can delete their own cards.
        Also deletes the associated image from GCS.

        Args:
            card_id: Card UUID
            owner_id: Owner's user ID (for authorization)

        Returns:
            True if deleted, False if not found or not owner

        Raises:
            ValueError: If card is currently being traded
        """
        # Find the card
        card = await self.card_repository.find_by_id(card_id)
        
        if not card:
            return False
        
        # Check ownership
        if card.owner_id != owner_id:
            return False
        
        # Prevent deletion of cards in active trades
        if card.status == card.STATUS_TRADING:
            raise ValueError("Cannot delete card that is currently in a trade")
        
        # Extract blob name from image URL
        if card.image_url:
            # URL format: https://storage.googleapis.com/{bucket}/{blob_name}
            # Extract blob_name: cards/{user_id}/{card_id}.jpg
            parts = card.image_url.split("/")
            if len(parts) >= 5:  # Ensure URL has expected structure
                blob_name = "/".join(parts[4:])  # Get everything after bucket name
                
                # Try to delete from GCS (ignore errors if file doesn't exist)
                try:
                    self.gcs_service.delete_blob(blob_name)
                except Exception:
                    # Continue with card deletion even if GCS deletion fails
                    pass
        
        # Delete card from database
        return await self.card_repository.delete(card_id)
