"""Media read URL schemas for Phase 9."""
from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel, Field


class ReadMediaUrlsRequest(BaseModel):
    """Request schema for batch reading media signed URLs."""

    media_asset_ids: List[UUID] = Field(
        ...,
        description="List of media asset IDs to get read URLs for",
        min_length=1,
        max_length=50,  # Limit batch size
        examples=[["123e4567-e89b-12d3-a456-426614174000"]],
    )


class ReadMediaUrlsResponse(BaseModel):
    """Response schema for batch reading media signed URLs."""

    urls: Dict[str, str] = Field(
        ...,
        description="Mapping of media_id to signed read URL",
        examples=[{"123e4567-e89b-12d3-a456-426614174000": "https://storage.googleapis.com/..."}],
    )
    expires_in_minutes: int = Field(
        ...,
        description="URL expiration time in minutes (all URLs have same expiration)",
        example=10,
    )


class ReadMediaUrlsResponseWrapper(BaseModel):
    """Envelope wrapper for read media URLs response."""

    data: ReadMediaUrlsResponse
    meta: None = None
    error: None = None
