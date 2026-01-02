"""
Posts Schemas for Posts Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.posts.domain.entities.city_code import CityCode


class CreatePostRequest(BaseModel):
    """Request schema for creating a post"""

    city_code: CityCode = Field(
        ...,
        description="City code - must be one of: TPE (Taipei), NTP (New Taipei), TAO (Taoyuan), TXG (Taichung), TNN (Tainan), KHH (Kaohsiung), HSZ (Hsinchu City), CYI (Chiayi City), and other Taiwan cities",
        examples=["TPE"],
    )
    title: str = Field(
        ...,
        max_length=120,
        description="Post title",
        examples=["Looking for BTS cards in Taipei"],
    )
    content: str = Field(
        ...,
        description="Post content",
        examples=["I have Jungkook cards and looking for V cards"],
    )
    idol: Optional[str] = Field(
        None,
        max_length=100,
        description="Idol name for filtering",
        examples=["Jungkook"],
    )
    idol_group: Optional[str] = Field(
        None,
        max_length=100,
        description="Idol group for filtering",
        examples=["BTS"],
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="Expiry datetime (defaults to 14 days from now)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "city_code": "TPE",
                "title": "Looking for BTS cards in Taipei",
                "content": "I have Jungkook cards and looking for V cards",
                "idol": "Jungkook",
                "idol_group": "BTS",
            }
        }


class PostResponse(BaseModel):
    """Response schema for post details"""

    id: UUID = Field(..., description="Post ID")
    owner_id: UUID = Field(..., description="Owner user ID")
    city_code: CityCode = Field(..., description="City code")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    idol: Optional[str] = Field(None, description="Idol name")
    idol_group: Optional[str] = Field(None, description="Idol group")
    status: str = Field(
        ...,
        description="Post status",
        examples=["open", "closed", "expired", "deleted"],
    )
    expires_at: datetime = Field(..., description="Expiry datetime")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "owner_id": "987e6543-e21b-12d3-a456-426614174000",
                "city_code": "TPE",
                "title": "Looking for BTS cards in Taipei",
                "content": "I have Jungkook cards and looking for V cards",
                "idol": "Jungkook",
                "idol_group": "BTS",
                "status": "open",
                "expires_at": "2024-02-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class PostListResponse(BaseModel):
    """Response schema for post list"""

    posts: List[PostResponse] = Field(..., description="List of posts")
    total: int = Field(..., description="Total number of posts")

    class Config:
        json_schema_extra = {
            "example": {
                "posts": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "owner_id": "987e6543-e21b-12d3-a456-426614174000",
                        "city_code": "TPE",
                        "title": "Looking for BTS cards",
                        "content": "I have Jungkook cards",
                        "idol": "Jungkook",
                        "idol_group": "BTS",
                        "status": "open",
                        "expires_at": "2024-02-01T00:00:00Z",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "total": 1,
            }
        }


class PostInterestResponse(BaseModel):
    """Response schema for post interest details"""

    id: UUID = Field(..., description="Interest ID")
    post_id: UUID = Field(..., description="Post ID")
    user_id: UUID = Field(..., description="User ID who expressed interest")
    status: str = Field(
        ...,
        description="Interest status",
        examples=["pending", "accepted", "rejected"],
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "post_id": "987e6543-e21b-12d3-a456-426614174000",
                "user_id": "456e7890-e12b-34d5-a678-901234567000",
                "status": "pending",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class PostInterestListResponse(BaseModel):
    """Response schema for post interest list"""

    interests: List[PostInterestResponse] = Field(..., description="List of interests")
    total: int = Field(..., description="Total number of interests")

    class Config:
        json_schema_extra = {
            "example": {
                "interests": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "post_id": "987e6543-e21b-12d3-a456-426614174000",
                        "user_id": "456e7890-e12b-34d5-a678-901234567000",
                        "status": "pending",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "total": 1,
            }
        }


class AcceptInterestResponse(BaseModel):
    """Response schema for accepting an interest"""

    interest_id: UUID = Field(..., description="Interest ID")
    friendship_created: bool = Field(
        ..., description="Whether a new friendship was created"
    )
    chat_room_id: UUID = Field(..., description="Chat room ID for conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "interest_id": "123e4567-e89b-12d3-a456-426614174000",
                "friendship_created": True,
                "chat_room_id": "987e6543-e21b-12d3-a456-426614174000",
            }
        }


# Envelope wrappers for standardized responses
class PostResponseWrapper(BaseModel):
    """Response wrapper for single post (standardized envelope)"""

    data: PostResponse
    meta: None = None
    error: None = None


class PostListResponseWrapper(BaseModel):
    """Response wrapper for post list (standardized envelope)"""

    data: PostListResponse
    meta: None = None
    error: None = None


class PostInterestResponseWrapper(BaseModel):
    """Response wrapper for single post interest (standardized envelope)"""

    data: PostInterestResponse
    meta: None = None
    error: None = None


class PostInterestListResponseWrapper(BaseModel):
    """Response wrapper for post interest list (standardized envelope)"""

    data: PostInterestListResponse
    meta: None = None
    error: None = None


class AcceptInterestResponseWrapper(BaseModel):
    """Response wrapper for accept interest response (standardized envelope)"""

    data: AcceptInterestResponse
    meta: None = None
    error: None = None
