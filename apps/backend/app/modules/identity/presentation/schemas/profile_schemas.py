"""
Profile Schemas for Identity Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    """Response schema for user profile"""

    id: UUID = Field(..., description="Profile ID")
    user_id: UUID = Field(..., description="User ID")
    nickname: Optional[str] = Field(None, description="User nickname", max_length=100)
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="User bio/description")
    region: Optional[str] = Field(None, description="User region", max_length=100)
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="User preferences (JSON)"
    )
    privacy_flags: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {
            "nearby_visible": True,
            "show_online": True,
            "allow_stranger_chat": True,
        },
        description="Privacy settings",
    )
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Profile last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "987e6543-e21b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "nickname": "CardCollector",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Love collecting K-pop cards!",
                "region": "Seoul",
                "preferences": {"language": "ko", "theme": "dark"},
                "privacy_flags": {
                    "nearby_visible": True,
                    "show_online": True,
                    "allow_stranger_chat": False,
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T12:30:00Z",
            }
        }


class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile"""

    nickname: Optional[str] = Field(None, description="User nickname", max_length=100)
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="User bio/description")
    region: Optional[str] = Field(None, description="User region", max_length=100)
    preferences: Optional[Dict[str, Any]] = Field(
        None, description="User preferences (JSON)"
    )
    privacy_flags: Optional[Dict[str, bool]] = Field(
        None, description="Privacy settings"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "NewNickname",
                "bio": "Updated bio",
                "privacy_flags": {
                    "nearby_visible": True,
                    "show_online": False,
                    "allow_stranger_chat": True,
                },
            }
        }


class ProfileResponseWrapper(BaseModel):
    """Response wrapper for profile data (standardized envelope)"""

    data: ProfileResponse
    meta: None = None
    error: None = None
