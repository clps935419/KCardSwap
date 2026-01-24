"""Media API request and response schemas."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Presign endpoint schemas
class CreateUploadUrlRequestSchema(BaseModel):
    """Request schema for creating upload URL."""
    content_type: str = Field(..., description="Content type of the file (e.g., image/jpeg)", example="image/jpeg")
    file_size_bytes: int = Field(..., gt=0, description="File size in bytes", example=1048576)
    filename: Optional[str] = Field(None, description="Original filename", example="card.jpg")


class CreateUploadUrlResponseSchema(BaseModel):
    """Response schema for upload URL."""
    media_id: UUID = Field(..., description="Media asset ID for confirmation")
    upload_url: str = Field(..., description="Presigned URL for uploading file")
    expires_in_minutes: int = Field(..., description="URL expiration time in minutes")


# Confirm endpoint schemas
class ConfirmUploadRequestSchema(BaseModel):
    """Request schema for confirming upload."""
    # media_id comes from path parameter


class ConfirmUploadResponseSchema(BaseModel):
    """Response schema after confirming upload."""
    media_id: UUID
    status: str = Field(..., description="Media status after confirmation", example="confirmed")
    file_size_bytes: int


# Attach endpoint schemas
class AttachMediaToPostRequestSchema(BaseModel):
    """Request schema for attaching media to post."""
    media_id: UUID = Field(..., description="ID of confirmed media to attach")


class AttachMediaToGalleryCardRequestSchema(BaseModel):
    """Request schema for attaching media to gallery card."""
    media_id: UUID = Field(..., description="ID of confirmed media to attach")


class AttachMediaResponseSchema(BaseModel):
    """Response schema after attaching media."""
    media_id: UUID
    status: str = Field(..., description="Media status after attachment", example="attached")
    attached_to: str = Field(..., description="Type of entity attached to", example="post")
    target_id: UUID = Field(..., description="ID of the entity media was attached to")
