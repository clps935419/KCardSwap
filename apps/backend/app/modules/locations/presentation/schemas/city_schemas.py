"""Schemas for city location endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class CityResponse(BaseModel):
    """Response schema for a single city."""

    code: str = Field(..., description="City code (e.g., TPE, NTP, TAO)")
    name: str = Field(..., description="English name (e.g., Taipei City)")
    name_zh: str = Field(..., description="Chinese name (e.g., 台北市)")

    model_config = ConfigDict(from_attributes=True)


class CityListResponse(BaseModel):
    """Response schema for list of all cities."""

    cities: list[CityResponse] = Field(..., description="List of all available Taiwan cities/counties")


# Envelope wrapper for standardized response
class CityListResponseWrapper(BaseModel):
    """Response wrapper for city list (standardized envelope)"""

    data: CityListResponse
    meta: None = None
    error: None = None
