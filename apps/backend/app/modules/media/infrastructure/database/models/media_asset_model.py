"""MediaAsset ORM model for Media module."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.shared.infrastructure.database.connection import Base


class MediaAssetModel(Base):
    """MediaAsset ORM model.

    Represents uploaded media files (images) that can be attached to posts or gallery cards.
    """

    __tablename__ = "media_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gcs_blob_name = Column(String(500), nullable=False, unique=True)  # Path in GCS bucket
    content_type = Column(String(100), nullable=False)  # e.g., image/jpeg
    file_size_bytes = Column(Integer, nullable=False)  # File size for quota calculation
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )  # pending, confirmed, attached
    target_type = Column(String(50), nullable=True)  # post, gallery_card (Phase 9)
    target_id = Column(UUID(as_uuid=True), nullable=True)  # ID of post or gallery_card (Phase 9)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    confirmed_at = Column(DateTime(timezone=True), nullable=True)  # When upload was confirmed
