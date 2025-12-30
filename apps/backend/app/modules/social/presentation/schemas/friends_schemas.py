"""
Friends Schemas for Social Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SendFriendRequestRequest(BaseModel):
    """Request schema for sending friend request"""

    friend_id: UUID = Field(
        ...,
        description="ID of user to send friend request to",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "friend_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }


class BlockUserRequest(BaseModel):
    """Request schema for blocking a user"""

    user_id: UUID = Field(
        ...,
        description="ID of user to block",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }


class UnblockUserRequest(BaseModel):
    """Request schema for unblocking a user"""

    user_id: UUID = Field(
        ...,
        description="ID of user to unblock",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }


class FriendshipResponse(BaseModel):
    """Response schema for friendship details"""

    id: UUID = Field(..., description="Friendship ID")
    user_id: UUID = Field(..., description="User ID")
    friend_id: UUID = Field(..., description="Friend ID")
    status: str = Field(
        ...,
        description="Friendship status",
        examples=["pending", "accepted", "blocked"],
    )
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-12d3-a456-426614174000",
                "friend_id": "456e7890-e12b-34d5-a678-901234567000",
                "status": "accepted",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class FriendListItemResponse(BaseModel):
    """Response schema for a single friend in the list"""

    user_id: UUID = Field(..., description="Friend's user ID")
    nickname: Optional[str] = Field(None, description="Friend's nickname")
    avatar_url: Optional[str] = Field(None, description="Friend's avatar URL")
    status: str = Field(..., description="Friendship status")
    created_at: datetime = Field(..., description="When friendship was created")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "456e7890-e12b-34d5-a678-901234567000",
                "nickname": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "status": "accepted",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class FriendListResponse(BaseModel):
    """Response schema for friend list"""

    friends: List[FriendListItemResponse] = Field(..., description="List of friends")
    total: int = Field(..., description="Total number of friends")

    class Config:
        json_schema_extra = {
            "example": {
                "friends": [
                    {
                        "user_id": "456e7890-e12b-34d5-a678-901234567000",
                        "nickname": "John Doe",
                        "avatar_url": "https://example.com/avatar.jpg",
                        "status": "accepted",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "total": 1,
            }
        }
