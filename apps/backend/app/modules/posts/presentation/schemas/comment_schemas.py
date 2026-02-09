"""
Comment Schemas for Posts Module
Presentation layer - Request/Response schemas for comments
"""

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class CreateCommentRequest(BaseModel):
    """Request schema for creating a comment"""

    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Comment content",
        examples=["Great post! I'm interested!"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Great post! I'm interested!",
            }
        }


class CommentResponse(BaseModel):
    """Response schema for comment details"""

    id: UUID = Field(..., description="Comment ID")
    post_id: UUID = Field(..., description="Post ID")
    user_id: UUID = Field(..., description="User ID who created the comment")
    content: str = Field(..., description="Comment content")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "post_id": "987e6543-e21b-12d3-a456-426614174000",
                "user_id": "456e7890-e12b-34d5-a678-901234567000",
                "content": "Great post! I'm interested!",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class CommentListResponse(BaseModel):
    """Response schema for comment list"""

    comments: List[CommentResponse] = Field(..., description="List of comments")
    total: int = Field(..., description="Total number of comments")

    class Config:
        json_schema_extra = {
            "example": {
                "comments": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "post_id": "987e6543-e21b-12d3-a456-426614174000",
                        "user_id": "456e7890-e12b-34d5-a678-901234567000",
                        "content": "Great post! I'm interested!",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "total": 1,
            }
        }


# Envelope wrappers for standardized responses
class CommentResponseWrapper(BaseModel):
    """Response wrapper for single comment (standardized envelope)"""

    data: CommentResponse
    meta: None = None
    error: None = None


class CommentListResponseWrapper(BaseModel):
    """Response wrapper for comment list (standardized envelope)"""

    data: CommentListResponse
    meta: None = None
    error: None = None
