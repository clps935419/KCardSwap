"""
Pydantic schemas for nearby search API.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SearchNearbyRequest(BaseModel):
    """Request schema for nearby card search"""

    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lng: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    radius_km: Optional[float] = Field(
        None, gt=0, le=100, description="Search radius in kilometers (max 100km)"
    )

    @field_validator("lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("lng")
    @classmethod
    def validate_lng(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v


class NearbyCardResponse(BaseModel):
    """Response schema for a nearby card result"""

    card_id: UUID = Field(..., description="Card unique identifier")
    owner_id: UUID = Field(..., description="Card owner's user ID")
    distance_km: float = Field(..., description="Distance from search origin in kilometers")
    idol: Optional[str] = Field(None, description="Idol name")
    idol_group: Optional[str] = Field(None, description="Idol group name")
    album: Optional[str] = Field(None, description="Album name")
    version: Optional[str] = Field(None, description="Card version")
    rarity: Optional[str] = Field(None, description="Card rarity")
    image_url: Optional[str] = Field(None, description="Card image URL")
    owner_nickname: Optional[str] = Field(None, description="Owner's nickname")

    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "123e4567-e89b-12d3-a456-426614174000",
                "owner_id": "987e6543-e21b-12d3-a456-426614174000",
                "distance_km": 2.5,
                "idol": "IU",
                "idol_group": "Solo",
                "album": "Lilac",
                "version": "Standard",
                "rarity": "rare",
                "image_url": "https://storage.googleapis.com/kcardswap/cards/...",
                "owner_nickname": "CardCollector123",
            }
        }


class SearchNearbyResponse(BaseModel):
    """Response schema for nearby search results"""

    results: List[NearbyCardResponse] = Field(
        ..., description="List of nearby cards"
    )
    count: int = Field(..., description="Number of results returned")

    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "card_id": "123e4567-e89b-12d3-a456-426614174000",
                        "owner_id": "987e6543-e21b-12d3-a456-426614174000",
                        "distance_km": 2.5,
                        "idol": "IU",
                        "idol_group": "Solo",
                        "album": "Lilac",
                        "version": "Standard",
                        "rarity": "rare",
                        "image_url": "https://storage.googleapis.com/kcardswap/cards/...",
                        "owner_nickname": "CardCollector123",
                    }
                ],
                "count": 1,
            }
        }


class UpdateLocationRequest(BaseModel):
    """Request schema for updating user location"""

    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lng: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")

    @field_validator("lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("lng")
    @classmethod
    def validate_lng(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v
