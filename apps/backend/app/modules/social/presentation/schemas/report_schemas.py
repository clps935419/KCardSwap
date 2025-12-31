"""
Report Schemas for Social Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.social.domain.entities.report import ReportReason


class ReportRequest(BaseModel):
    """Request schema for submitting a report"""
    
    model_config = ConfigDict(use_enum_values=True)

    reported_user_id: UUID = Field(
        ...,
        description="ID of user being reported",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    reason: ReportReason = Field(
        ...,
        description="Reason for report (must be one of: fraud, fake_card, harassment, inappropriate_content, spam, other)",
        examples=["harassment"],
    )
    detail: Optional[str] = Field(
        None,
        description="Detailed description of the issue",
        max_length=1000,
        examples=["User sent inappropriate messages and refused to complete trade."],
    )


class ReportResponse(BaseModel):
    """Response schema for a report"""
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID = Field(..., description="Report ID")
    reporter_id: UUID = Field(..., description="User who filed the report")
    reported_user_id: UUID = Field(..., description="User who was reported")
    reason: ReportReason = Field(..., description="Reason for report")
    detail: Optional[str] = Field(None, description="Detailed description")
    status: str = Field(
        ...,
        description="Report status",
        examples=["pending", "reviewed", "resolved"],
    )
    created_at: datetime = Field(..., description="Creation timestamp")


class ReportListResponse(BaseModel):
    """Response schema for list of reports"""

    reports: List[ReportResponse] = Field(..., description="List of reports")
    total: int = Field(..., description="Total number of reports")
