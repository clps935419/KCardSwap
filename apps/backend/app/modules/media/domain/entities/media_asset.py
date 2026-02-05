"""MediaAsset domain entity for User Story 3.

Represents a media file (image) that can be attached to posts or gallery cards.
Follows presign → upload → confirm → attach flow.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID


class MediaStatus(str, Enum):
    """Media upload status."""
    PENDING = "pending"  # Presigned URL generated, waiting for upload confirmation
    CONFIRMED = "confirmed"  # Upload confirmed, ready to be attached
    ATTACHED = "attached"  # Attached to a post or gallery card


class MediaAsset:
    """Domain entity representing a media asset.

    Media assets follow a strict lifecycle:
    1. PENDING: Presigned URL created, user uploads to GCS
    2. CONFIRMED: User confirms upload, quota applied
    3. ATTACHED: Media attached to post or gallery card

    FR-007: Only confirmed media owned by the user can be attached.
    FR-022: Quota is only applied on confirmation, not on presign.
    """

    def __init__(
        self,
        id: UUID,
        owner_id: UUID,
        gcs_blob_name: str,
        content_type: str,
        file_size_bytes: int,
        status: MediaStatus,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        confirmed_at: Optional[datetime] = None,
        target_type: Optional[str] = None,
        target_id: Optional[UUID] = None,
    ):
        self.id = id
        self.owner_id = owner_id
        self.gcs_blob_name = gcs_blob_name
        self.content_type = content_type
        self.file_size_bytes = file_size_bytes
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.confirmed_at = confirmed_at
        self.target_type = target_type
        self.target_id = target_id

    def confirm(self) -> None:
        """Confirm the upload - moves from PENDING to CONFIRMED.

        FR-022: Quota is applied when this method is called.
        """
        if self.status != MediaStatus.PENDING:
            raise ValueError(f"Cannot confirm media with status {self.status}")
        self.status = MediaStatus.CONFIRMED
        self.confirmed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def attach(self, target_type: str, target_id: UUID) -> None:
        """Mark media as attached to a post or gallery card.

        FR-007: Only confirmed media can be attached.
        
        Args:
            target_type: Type of target entity ("post" or "gallery_card")
            target_id: ID of the target entity
        """
        if self.status != MediaStatus.CONFIRMED:
            raise ValueError(f"Cannot attach media with status {self.status}. Media must be confirmed first.")
        self.status = MediaStatus.ATTACHED
        self.target_type = target_type
        self.target_id = target_id
        self.updated_at = datetime.now(timezone.utc)

    def is_confirmed(self) -> bool:
        """Check if media is confirmed and ready to attach."""
        return self.status == MediaStatus.CONFIRMED

    def is_owned_by(self, user_id: UUID) -> bool:
        """Check if media is owned by the given user.

        FR-007: Media can only be attached by its owner.
        """
        return self.owner_id == user_id

    def __repr__(self) -> str:
        return f"<MediaAsset(id={self.id}, owner_id={self.owner_id}, status={self.status})>"
