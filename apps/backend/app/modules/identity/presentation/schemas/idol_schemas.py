"""Schemas for idol group endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class IdolGroupResponse(BaseModel):
    """Response schema for a single idol group."""

    id: str = Field(..., description="Idol group ID (e.g., newjeans, ive, aespa)")
    name: str = Field(..., description="Idol group name (e.g., NewJeans, IVE, aespa)")
    emoji: str = Field(..., description="Emoji representing the idol group (e.g., 👖, 🦢, 🦋)")

    model_config = ConfigDict(from_attributes=True)


class IdolGroupListResponse(BaseModel):
    """Response schema for list of all idol groups."""

    groups: list[IdolGroupResponse] = Field(
        ..., description="List of all available idol groups for onboarding"
    )


# Envelope wrapper for standardized response
class IdolGroupListResponseWrapper(BaseModel):
    """Response wrapper for idol group list (standardized envelope)"""

    data: IdolGroupListResponse
    meta: None = None
    error: None = None
