"""
Posts Schemas for Posts Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.modules.posts.domain.entities.city_code import CityCode
from app.modules.posts.domain.entities.post_enums import PostCategory, PostScope


class CreatePostRequest(BaseModel):
    """Request schema for creating a post (V2: with scope/category)"""

    scope: PostScope = Field(
        ...,
        description="Post scope: global (visible everywhere) or city (city-specific)",
        examples=["global", "city"],
    )
    city_code: Optional[CityCode] = Field(
        None,
        description="City code - required when scope=city, must be empty when scope=global",
        examples=["TPE"],
    )
    category: PostCategory = Field(
        ...,
        description="Post category",
        examples=["trade", "giveaway", "group", "showcase", "help", "announcement"],
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

    @field_validator("city_code")
    @classmethod
    def validate_city_code_with_scope(cls, v, info):
        """Validate FR-004: scope=city requires city_code"""
        scope = info.data.get("scope")
        if scope == PostScope.CITY and not v:
            raise ValueError("city_code is required when scope is 'city'")
        if scope == PostScope.GLOBAL and v:
            raise ValueError("city_code must be empty when scope is 'global'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "scope": "city",
                "city_code": "TPE",
                "category": "trade",
                "title": "Looking for BTS cards in Taipei",
                "content": "I have Jungkook cards and looking for V cards",
                "idol": "Jungkook",
                "idol_group": "BTS",
            }
        }


class PostResponse(BaseModel):
    """Response schema for post details (V2: with scope/category + like fields)"""

    id: UUID = Field(..., description="Post ID")
    owner_id: UUID = Field(..., description="Owner user ID")
    scope: str = Field(..., description="Post scope (global/city)")
    city_code: Optional[str] = Field(None, description="City code (if scope=city)")
    category: str = Field(..., description="Post category")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    idol: Optional[str] = Field(None, description="Idol name")
    idol_group: Optional[str] = Field(None, description="Idol group")
    status: str = Field(
        ...,
        description="Post status",
        examples=["open", "closed", "expired", "deleted"],
    )
    like_count: int = Field(0, description="Total number of likes on this post")
    liked_by_me: bool = Field(False, description="Whether the current user has liked this post")
    media_asset_ids: List[UUID] = Field(
        default_factory=list,
        description="List of media asset IDs attached to this post (Phase 9)",
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
                "scope": "city",
                "city_code": "TPE",
                "category": "trade",
                "title": "Looking for BTS cards in Taipei",
                "content": "I have Jungkook cards and looking for V cards",
                "idol": "Jungkook",
                "idol_group": "BTS",
                "status": "open",
                "like_count": 5,
                "liked_by_me": True,
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
                        "scope": "city",
                        "city_code": "TPE",
                        "category": "trade",
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


class ToggleLikeResponse(BaseModel):
    """Response schema for toggle like action"""

    liked: bool = Field(..., description="Whether the post is now liked by the user")
    like_count: int = Field(..., description="Current total like count for the post")

    class Config:
        json_schema_extra = {
            "example": {
                "liked": True,
                "like_count": 6,
            }
        }


class ToggleLikeResponseWrapper(BaseModel):
    """Response wrapper for toggle like response (standardized envelope)"""

    data: ToggleLikeResponse
    meta: None = None
    error: None = None
