"""
Report Schemas for Social Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Request schema for submitting a report"""

    reported_user_id: UUID = Field(
        ...,
        description="ID of user being reported",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    reason: str = Field(
        ...,
        description="Reason for report",
        min_length=1,
        max_length=100,
        examples=["Inappropriate behavior", "Spam", "Scam", "Harassment"],
    )
    detail: Optional[str] = Field(
        None,
        description="Detailed description of the issue",
        max_length=1000,
        examples=["User sent inappropriate messages and refused to complete trade."],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reported_user_id": "123e4567-e89b-12d3-a456-426614174000",
                "reason": "Inappropriate behavior",
                "detail": "User sent inappropriate messages and refused to complete trade.",
            }
        }


class ReportResponse(BaseModel):
    """Response schema for a report"""

    id: UUID = Field(..., description="Report ID")
    reporter_id: UUID = Field(..., description="User who filed the report")
    reported_user_id: UUID = Field(..., description="User who was reported")
    reason: str = Field(..., description="Reason for report")
    detail: Optional[str] = Field(None, description="Detailed description")
    status: str = Field(
        ...,
        description="Report status",
        examples=["pending", "reviewed", "resolved"],
    )
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "456e7890-e12b-34d5-a678-901234567000",
                "reporter_id": "789e0123-e45b-67d8-a901-234567890000",
                "reported_user_id": "123e4567-e89b-12d3-a456-426614174000",
                "reason": "Inappropriate behavior",
                "detail": "User sent inappropriate messages.",
                "status": "pending",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class ReportListResponse(BaseModel):
    """Response schema for list of reports"""

    reports: List[ReportResponse] = Field(..., description="List of reports")
    total: int = Field(..., description="Total number of reports")

    class Config:
        json_schema_extra = {
            "example": {
                "reports": [
                    {
                        "id": "456e7890-e12b-34d5-a678-901234567000",
                        "reporter_id": "789e0123-e45b-67d8-a901-234567890000",
                        "reported_user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "reason": "Inappropriate behavior",
                        "detail": "User sent inappropriate messages.",
                        "status": "pending",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "total": 1,
            }
        }
