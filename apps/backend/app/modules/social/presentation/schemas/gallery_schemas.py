"""
Pydantic schemas for Gallery Card endpoints.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateGalleryCardRequest(BaseModel):
    """Request to create a gallery card."""

    title: str = Field(..., min_length=1, max_length=200)
    idol_name: str = Field(..., min_length=1, max_length=100)
    era: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class GalleryCardResponse(BaseModel):
    """Response for a single gallery card."""

    id: UUID
    user_id: UUID
    title: str
    idol_name: str
    era: Optional[str] = None
    description: Optional[str] = None
    media_asset_id: Optional[UUID] = None
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GalleryCardListResponse(BaseModel):
    """Response for a list of gallery cards."""

    items: List[GalleryCardResponse]
    total: int


class ReorderGalleryCardsRequest(BaseModel):
    """Request to reorder gallery cards."""

    card_ids: List[UUID] = Field(..., min_items=1)


class ReorderGalleryCardsResponse(BaseModel):
    """Response after reordering gallery cards."""

    message: str = "Gallery cards reordered successfully"
    updated_count: int


# Envelope wrappers for standardized responses
class GalleryCardResponseWrapper(BaseModel):
    """Response wrapper for single gallery card (standardized envelope)"""

    data: GalleryCardResponse
    meta: None = None
    error: None = None


class GalleryCardListResponseWrapper(BaseModel):
    """Response wrapper for gallery card list (standardized envelope)"""

    data: GalleryCardListResponse
    meta: None = None
    error: None = None


class ReorderGalleryCardsResponseWrapper(BaseModel):
    """Response wrapper for reorder response (standardized envelope)"""

    data: ReorderGalleryCardsResponse
    meta: None = None
    error: None = None
