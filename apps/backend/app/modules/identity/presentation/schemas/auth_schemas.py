"""
Authentication Schemas for Identity Module
Presentation layer - Request/Response schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class GoogleLoginRequest(BaseModel):
    """Request schema for Google login"""
    google_token: str = Field(
        ...,
        description="Google ID token received from Google OAuth",
        min_length=1
    )


class GoogleCallbackRequest(BaseModel):
    """Request schema for Google OAuth callback with PKCE (Expo AuthSession)"""
    code: str = Field(
        ...,
        description="Authorization code from Google OAuth",
        min_length=1
    )
    code_verifier: str = Field(
        ...,
        description="PKCE code verifier used during authorization request",
        min_length=43,
        max_length=128
    )
    redirect_uri: Optional[str] = Field(
        None,
        description="Redirect URI used during authorization (must match the one used in auth request)"
    )


class TokenResponse(BaseModel):
    """Response schema for authentication tokens"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user_id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token"""
    refresh_token: str = Field(
        ...,
        description="Refresh token",
        min_length=1
    )


class LogoutRequest(BaseModel):
    """Request schema for logout (optional refresh token to revoke)"""
    refresh_token: Optional[str] = Field(
        None,
        description="Optional refresh token to revoke"
    )


class LoginResponse(BaseModel):
    """Response wrapper for successful login"""
    data: TokenResponse
    error: None = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorWrapper(BaseModel):
    """Error wrapper response"""
    data: None = None
    error: ErrorResponse
