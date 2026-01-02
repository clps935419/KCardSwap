"""
Rating Schemas for Social Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RatingRequest(BaseModel):
    """Request schema for submitting a rating"""

    rated_user_id: UUID = Field(
        ...,
        description="ID of user being rated",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    trade_id: Optional[UUID] = Field(
        None,
        description="Associated trade ID (optional)",
        examples=["987e6543-e21b-12d3-a456-426614174000"],
    )
    score: int = Field(
        ...,
        description="Rating score (1-5)",
        ge=1,
        le=5,
        examples=[5],
    )
    comment: Optional[str] = Field(
        None,
        description="Optional comment",
        max_length=500,
        examples=["Great trader! Fast and friendly communication."],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rated_user_id": "123e4567-e89b-12d3-a456-426614174000",
                "trade_id": "987e6543-e21b-12d3-a456-426614174000",
                "score": 5,
                "comment": "Great trader! Fast and friendly communication.",
            }
        }


class RatingResponse(BaseModel):
    """Response schema for a rating"""

    id: UUID = Field(..., description="Rating ID")
    rater_id: UUID = Field(..., description="User who gave the rating")
    rated_user_id: UUID = Field(..., description="User who received the rating")
    trade_id: Optional[UUID] = Field(None, description="Associated trade ID")
    score: int = Field(..., description="Rating score (1-5)")
    comment: Optional[str] = Field(None, description="Rating comment")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "456e7890-e12b-34d5-a678-901234567000",
                "rater_id": "789e0123-e45b-67d8-a901-234567890000",
                "rated_user_id": "123e4567-e89b-12d3-a456-426614174000",
                "trade_id": "987e6543-e21b-12d3-a456-426614174000",
                "score": 5,
                "comment": "Great trader! Fast and friendly communication.",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class RatingListResponse(BaseModel):
    """Response schema for list of ratings"""

    ratings: List[RatingResponse] = Field(..., description="List of ratings")
    total: int = Field(..., description="Total number of ratings")

    class Config:
        json_schema_extra = {
            "example": {
                "ratings": [
                    {
                        "id": "456e7890-e12b-34d5-a678-901234567000",
                        "rater_id": "789e0123-e45b-67d8-a901-234567890000",
                        "rated_user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "trade_id": "987e6543-e21b-12d3-a456-426614174000",
                        "score": 5,
                        "comment": "Great trader!",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "total": 1,
            }
        }


class AverageRatingResponse(BaseModel):
    """Response schema for average rating"""

    user_id: UUID = Field(..., description="User ID")
    average_score: float = Field(
        ..., description="Average rating score", examples=[4.8]
    )
    total_ratings: int = Field(..., description="Total number of ratings received")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "average_score": 4.8,
                "total_ratings": 15,
            }
        }


# Envelope wrappers for standardized responses
class RatingResponseWrapper(BaseModel):
    """Response wrapper for single rating (standardized envelope)"""

    data: RatingResponse
    meta: None = None
    error: None = None


class RatingListResponseWrapper(BaseModel):
    """Response wrapper for rating list (standardized envelope)"""

    data: RatingListResponse
    meta: None = None
    error: None = None


class AverageRatingResponseWrapper(BaseModel):
    """Response wrapper for average rating (standardized envelope)"""

    data: AverageRatingResponse
    meta: None = None
    error: None = None
