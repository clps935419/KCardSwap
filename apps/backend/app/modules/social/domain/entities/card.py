"""
Card Entity - Core domain model for photo cards
Following DDD principles: No framework dependencies, pure business logic
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Card:
    """
    Card entity representing a collectible photo card.
    Contains core card information and business logic.
    """

    # Valid card statuses
    STATUS_AVAILABLE = "available"
    STATUS_TRADING = "trading"
    STATUS_TRADED = "traded"

    VALID_STATUSES = {STATUS_AVAILABLE, STATUS_TRADING, STATUS_TRADED}

    # Valid upload statuses
    UPLOAD_STATUS_PENDING = "pending"
    UPLOAD_STATUS_CONFIRMED = "confirmed"

    VALID_UPLOAD_STATUSES = {UPLOAD_STATUS_PENDING, UPLOAD_STATUS_CONFIRMED}

    # Valid rarities
    RARITY_COMMON = "common"
    RARITY_RARE = "rare"
    RARITY_EPIC = "epic"
    RARITY_LEGENDARY = "legendary"

    VALID_RARITIES = {RARITY_COMMON, RARITY_RARE, RARITY_EPIC, RARITY_LEGENDARY}

    def __init__(
        self,
        owner_id: UUID,
        idol: Optional[str] = None,
        idol_group: Optional[str] = None,
        album: Optional[str] = None,
        version: Optional[str] = None,
        rarity: Optional[str] = None,
        status: str = STATUS_AVAILABLE,
        image_url: Optional[str] = None,
        size_bytes: Optional[int] = None,
        upload_status: str = UPLOAD_STATUS_PENDING,
        upload_confirmed_at: Optional[datetime] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = id or uuid4()
        self._owner_id = owner_id
        self._idol = idol
        self._idol_group = idol_group
        self._album = album
        self._version = version
        self._rarity = rarity
        self._status = status
        self._image_url = image_url
        self._size_bytes = size_bytes
        self._upload_status = upload_status
        self._upload_confirmed_at = upload_confirmed_at
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

        self._validate()

    def _validate(self):
        """Validate card data"""
        if not self._owner_id:
            raise ValueError("owner_id is required")

        if self._status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}"
            )

        if self._upload_status not in self.VALID_UPLOAD_STATUSES:
            raise ValueError(
                f"Invalid upload_status. Must be one of: {', '.join(self.VALID_UPLOAD_STATUSES)}"
            )

        if self._rarity is not None and self._rarity not in self.VALID_RARITIES:
            raise ValueError(
                f"Invalid rarity. Must be one of: {', '.join(self.VALID_RARITIES)}"
            )

        if self._size_bytes is not None and self._size_bytes < 0:
            raise ValueError("size_bytes must be non-negative")

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def owner_id(self) -> UUID:
        return self._owner_id

    @property
    def idol(self) -> Optional[str]:
        return self._idol

    @property
    def idol_group(self) -> Optional[str]:
        return self._idol_group

    @property
    def album(self) -> Optional[str]:
        return self._album

    @property
    def version(self) -> Optional[str]:
        return self._version

    @property
    def rarity(self) -> Optional[str]:
        return self._rarity

    @property
    def status(self) -> str:
        return self._status

    @property
    def image_url(self) -> Optional[str]:
        return self._image_url

    @property
    def size_bytes(self) -> Optional[int]:
        return self._size_bytes

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def upload_status(self) -> str:
        return self._upload_status

    @property
    def upload_confirmed_at(self) -> Optional[datetime]:
        return self._upload_confirmed_at

    def is_available(self) -> bool:
        """Check if card is available for trading"""
        return self._status == self.STATUS_AVAILABLE

    def mark_as_trading(self):
        """Mark card as being in a trade"""
        if self._status == self.STATUS_TRADED:
            raise ValueError("Cannot trade an already traded card")
        self._status = self.STATUS_TRADING
        self._updated_at = datetime.utcnow()

    def mark_as_traded(self):
        """Mark card as traded (completed)"""
        self._status = self.STATUS_TRADED
        self._updated_at = datetime.utcnow()

    def mark_as_available(self):
        """Mark card as available again"""
        if self._status == self.STATUS_TRADED:
            raise ValueError("Cannot make a traded card available again")
        self._status = self.STATUS_AVAILABLE
        self._updated_at = datetime.utcnow()

    def update_image(self, image_url: str, size_bytes: int):
        """Update card image URL and size"""
        if size_bytes < 0:
            raise ValueError("size_bytes must be non-negative")
        self._image_url = image_url
        self._size_bytes = size_bytes
        self._updated_at = datetime.utcnow()

    def confirm_upload(self):
        """Confirm that the card image has been successfully uploaded to GCS"""
        if self._upload_status == self.UPLOAD_STATUS_CONFIRMED:
            raise ValueError("Upload already confirmed")
        self._upload_status = self.UPLOAD_STATUS_CONFIRMED
        self._upload_confirmed_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    def is_upload_confirmed(self) -> bool:
        """Check if upload has been confirmed"""
        return self._upload_status == self.UPLOAD_STATUS_CONFIRMED

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"Card(id={self._id}, owner_id={self._owner_id}, status={self._status})"
