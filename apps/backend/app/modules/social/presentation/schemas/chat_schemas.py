"""
Chat Schemas for Social Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """Request schema for sending a message"""

    content: str = Field(
        ...,
        description="Message content",
        min_length=1,
        max_length=2000,
        examples=["Hello! I'm interested in trading cards."],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello! I'm interested in trading cards.",
            }
        }


class MessageResponse(BaseModel):
    """Response schema for a single message"""

    id: UUID = Field(..., description="Message ID")
    room_id: UUID = Field(..., description="Chat room ID")
    sender_id: UUID = Field(..., description="Sender user ID")
    content: str = Field(..., description="Message content")
    status: str = Field(
        ...,
        description="Message status",
        examples=["sent", "delivered", "read"],
    )
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "room_id": "987e6543-e21b-12d3-a456-426614174000",
                "sender_id": "456e7890-e12b-34d5-a678-901234567000",
                "content": "Hello! I'm interested in trading cards.",
                "status": "sent",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class GetMessagesRequest(BaseModel):
    """Request schema for getting messages"""

    after_message_id: Optional[UUID] = Field(
        None,
        description="Get messages after this message ID (for pagination)",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    limit: int = Field(
        50,
        description="Maximum number of messages to return",
        ge=1,
        le=100,
        examples=[50],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "after_message_id": "123e4567-e89b-12d3-a456-426614174000",
                "limit": 50,
            }
        }


class ChatRoomParticipantResponse(BaseModel):
    """Response schema for chat room participant"""

    user_id: UUID = Field(..., description="User ID")
    nickname: Optional[str] = Field(None, description="User's nickname")
    avatar_url: Optional[str] = Field(None, description="User's avatar URL")

    class Config:
        from_attributes = True


class ChatRoomResponse(BaseModel):
    """Response schema for chat room details"""

    id: UUID = Field(..., description="Chat room ID")
    participants: List[ChatRoomParticipantResponse] = Field(
        ..., description="Room participants"
    )
    last_message: Optional[MessageResponse] = Field(
        None, description="Last message in the room"
    )
    unread_count: int = Field(
        0, description="Number of unread messages for current user"
    )
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "987e6543-e21b-12d3-a456-426614174000",
                "participants": [
                    {
                        "user_id": "456e7890-e12b-34d5-a678-901234567000",
                        "nickname": "John Doe",
                        "avatar_url": "https://example.com/avatar.jpg",
                    },
                    {
                        "user_id": "789e0123-e45b-67d8-a901-234567890000",
                        "nickname": "Jane Smith",
                        "avatar_url": "https://example.com/avatar2.jpg",
                    },
                ],
                "last_message": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "room_id": "987e6543-e21b-12d3-a456-426614174000",
                    "sender_id": "456e7890-e12b-34d5-a678-901234567000",
                    "content": "Hello!",
                    "status": "read",
                    "created_at": "2024-01-01T00:00:00Z",
                },
                "unread_count": 0,
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class MessagesListResponse(BaseModel):
    """Response schema for list of messages"""

    messages: List[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")
    has_more: bool = Field(
        ..., description="Whether there are more messages to fetch"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "room_id": "987e6543-e21b-12d3-a456-426614174000",
                        "sender_id": "456e7890-e12b-34d5-a678-901234567000",
                        "content": "Hello!",
                        "status": "read",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "total": 1,
                "has_more": False,
            }
        }
