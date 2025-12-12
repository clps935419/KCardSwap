"""
Pydantic schemas for API requests and responses
"""
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Auth Schemas
class GoogleLoginRequest(BaseModel):
    """Google login request"""
    google_token: str = Field(..., description="Google ID token")


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# Profile Schemas
class ProfileResponse(BaseModel):
    """Profile response"""
    user_id: UUID
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    region: Optional[str] = None
    preferences: Dict[str, Any] = {}
    privacy_flags: Dict[str, bool] = {}

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    nickname: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=1000)
    region: Optional[str] = Field(None, max_length=100)
    preferences: Optional[Dict[str, Any]] = None
    privacy_flags: Optional[Dict[str, bool]] = None


# Standard API Response
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    data: Optional[Any] = None
    error: Optional[Dict[str, str]] = None


class ErrorDetail(BaseModel):
    """Error detail"""
    code: str
    message: str
