"""
Confirm Card Upload Use Case - Verify GCS object exists and mark upload as confirmed
"""

from uuid import UUID

from app.modules.social.domain.repositories.i_card_repository import ICardRepository


class ConfirmCardUploadUseCase:
    """
    Use case for confirming card image upload after successful GCS upload.
    Validates that the object exists in GCS and marks the card as confirmed.
    """

    def __init__(
        self,
        card_repository: ICardRepository,
        gcs_service,  # GCSStorageService or MockGCSStorageService
    ):
        self.card_repository = card_repository
        self.gcs_service = gcs_service

    async def execute(self, card_id: UUID, owner_id: UUID) -> bool:
        """
        Confirm card upload by verifying GCS object exists.

        Args:
            card_id: ID of the card to confirm
            owner_id: ID of the card owner (for authorization)

        Returns:
            True if confirmation successful

        Raises:
            ValueError: If card not found, not owned by user, already confirmed,
                       or GCS object doesn't exist
        """
        # Find card
        card = await self.card_repository.find_by_id(card_id)
        if not card:
            raise ValueError("Card not found")

        # Verify ownership
        if card.owner_id != owner_id:
            raise ValueError("Not authorized to confirm this card")

        # Check if already confirmed
        if card.is_upload_confirmed():
            raise ValueError("Upload already confirmed")

        # Verify GCS object exists
        if not card.image_url:
            raise ValueError("Card has no image URL")

        # Extract blob name from image URL
        # Format: https://storage.googleapis.com/{bucket}/{blob_name}
        blob_name = self._extract_blob_name(card.image_url)

        # Check if blob exists in GCS
        exists = self.gcs_service.blob_exists(blob_name)
        if not exists:
            raise ValueError(
                "Image file not found in storage. Please upload the file first."
            )

        # Mark as confirmed
        card.confirm_upload()
        await self.card_repository.save(card)

        return True

    def _extract_blob_name(self, image_url: str) -> str:
        """
        Extract blob name from GCS public URL.

        Args:
            image_url: Full GCS URL (e.g., https://storage.googleapis.com/bucket/path/file.jpg)

        Returns:
            Blob name (e.g., path/file.jpg)
        """
        # Remove the GCS domain and bucket name
        # Format: https://storage.googleapis.com/{bucket}/{blob_name}
        parts = image_url.split("/")
        if len(parts) >= 5 and "storage.googleapis.com" in image_url:
            # Join everything after the bucket name
            return "/".join(parts[4:])

        # Fallback: assume the URL is already a blob name
        return image_url
