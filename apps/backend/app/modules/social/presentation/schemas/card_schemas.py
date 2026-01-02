"""
Card Schemas for Social Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UploadCardRequest(BaseModel):
    """Request schema for getting upload signed URL"""

    content_type: str = Field(
        ...,
        description="MIME type of the file (image/jpeg or image/png)",
        examples=["image/jpeg", "image/png"],
    )
    file_size_bytes: int = Field(
        ..., description="Size of file in bytes", gt=0, examples=[1234567]
    )
    idol: Optional[str] = Field(None, description="Idol name", max_length=100)
    idol_group: Optional[str] = Field(None, description="Idol group", max_length=100)
    album: Optional[str] = Field(None, description="Album name", max_length=100)
    version: Optional[str] = Field(None, description="Version", max_length=100)
    rarity: Optional[str] = Field(
        None,
        description="Card rarity",
        examples=["common", "rare", "epic", "legendary"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "image/jpeg",
                "file_size_bytes": 1234567,
                "idol": "IU",
                "idol_group": "Solo",
                "album": "Love Poem",
                "version": "Version A",
                "rarity": "rare",
            }
        }


class UploadUrlResponse(BaseModel):
    """Response schema for upload signed URL"""

    upload_url: str = Field(..., description="Signed URL for uploading")
    method: str = Field(..., description="HTTP method to use", examples=["PUT"])
    required_headers: Dict[str, str] = Field(
        ..., description="Required headers for upload"
    )
    image_url: str = Field(..., description="Public URL of the image after upload")
    expires_at: datetime = Field(..., description="When the signed URL expires")
    card_id: UUID = Field(..., description="ID of the created card")

    class Config:
        json_schema_extra = {
            "example": {
                "upload_url": "https://storage.googleapis.com/bucket/path?signature=...",
                "method": "PUT",
                "required_headers": {"Content-Type": "image/jpeg"},
                "image_url": "https://storage.googleapis.com/bucket/cards/user_id/card_id.jpg",
                "expires_at": "2025-01-01T00:15:00Z",
                "card_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }


class CardResponse(BaseModel):
    """Response schema for card details"""

    id: UUID = Field(..., description="Card ID")
    owner_id: UUID = Field(..., description="Owner user ID")
    idol: Optional[str] = Field(None, description="Idol name")
    idol_group: Optional[str] = Field(None, description="Idol group")
    album: Optional[str] = Field(None, description="Album name")
    version: Optional[str] = Field(None, description="Version")
    rarity: Optional[str] = Field(None, description="Card rarity")
    status: str = Field(..., description="Card status")
    image_url: Optional[str] = Field(None, description="Image URL")
    size_bytes: Optional[int] = Field(None, description="Image size in bytes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "owner_id": "987e6543-e21b-12d3-a456-426614174000",
                "idol": "IU",
                "idol_group": "Solo",
                "album": "Love Poem",
                "version": "Version A",
                "rarity": "rare",
                "status": "available",
                "image_url": "https://storage.googleapis.com/bucket/cards/user_id/card_id.jpg",
                "size_bytes": 1234567,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class QuotaStatusResponse(BaseModel):
    """Response schema for quota status"""

    uploads_today: int = Field(..., description="Number of uploads today")
    daily_limit: int = Field(..., description="Daily upload limit")
    remaining_uploads: int = Field(..., description="Remaining uploads for today")
    storage_used_bytes: int = Field(..., description="Total storage used in bytes")
    storage_limit_bytes: int = Field(..., description="Storage limit in bytes")
    remaining_storage_bytes: int = Field(..., description="Remaining storage in bytes")
    storage_used_mb: float = Field(..., description="Storage used in MB")
    storage_limit_mb: float = Field(..., description="Storage limit in MB")
    remaining_storage_mb: float = Field(..., description="Remaining storage in MB")

    class Config:
        json_schema_extra = {
            "example": {
                "uploads_today": 1,
                "daily_limit": 2,
                "remaining_uploads": 1,
                "storage_used_bytes": 5242880,
                "storage_limit_bytes": 1073741824,
                "remaining_storage_bytes": 1068498944,
                "storage_used_mb": 5.0,
                "storage_limit_mb": 1024.0,
                "remaining_storage_mb": 1019.0,
            }
        }


# Envelope wrappers for standardized responses
class UploadUrlResponseWrapper(BaseModel):
    """Response wrapper for upload URL (standardized envelope)"""

    data: UploadUrlResponse
    meta: None = None
    error: None = None


class CardResponseWrapper(BaseModel):
    """Response wrapper for single card (standardized envelope)"""

    data: CardResponse
    meta: None = None
    error: None = None


class CardListResponseWrapper(BaseModel):
    """Response wrapper for card list (standardized envelope)"""

    data: list[CardResponse]
    meta: None = None
    error: None = None


class QuotaStatusResponseWrapper(BaseModel):
    """Response wrapper for quota status (standardized envelope)"""

    data: QuotaStatusResponse
    meta: None = None
    error: None = None


class DeleteSuccessResponse(BaseModel):
    """Success response for delete operations"""

    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")


class DeleteSuccessResponseWrapper(BaseModel):
    """Response wrapper for delete success (standardized envelope)"""

    data: DeleteSuccessResponse
    meta: None = None
    error: None = None
