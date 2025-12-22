"""
Trade Schemas for Social Module
Presentation layer - Request/Response schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateTradeRequest(BaseModel):
    """Request schema for creating a trade proposal"""

    responder_id: UUID = Field(..., description="User ID of the responder")
    initiator_card_ids: List[UUID] = Field(
        ...,
        description="List of card IDs from initiator",
        min_length=1,
        examples=[["123e4567-e89b-12d3-a456-426614174000"]],
    )
    responder_card_ids: List[UUID] = Field(
        ...,
        description="List of card IDs from responder",
        min_length=1,
        examples=[["223e4567-e89b-12d3-a456-426614174000"]],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "responder_id": "323e4567-e89b-12d3-a456-426614174000",
                "initiator_card_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "124e4567-e89b-12d3-a456-426614174000",
                ],
                "responder_card_ids": [
                    "223e4567-e89b-12d3-a456-426614174000",
                    "224e4567-e89b-12d3-a456-426614174000",
                ],
            }
        }


class TradeItemResponse(BaseModel):
    """Response schema for a trade item"""

    id: UUID = Field(..., description="Trade item ID")
    trade_id: UUID = Field(..., description="Trade ID")
    card_id: UUID = Field(..., description="Card ID")
    owner_side: str = Field(
        ...,
        description="Which party owns this card",
        examples=["initiator", "responder"],
    )
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    """Response schema for trade details"""

    id: UUID = Field(..., description="Trade ID")
    initiator_id: UUID = Field(..., description="Initiator user ID")
    responder_id: UUID = Field(..., description="Responder user ID")
    status: str = Field(
        ...,
        description="Trade status",
        examples=[
            "draft",
            "proposed",
            "accepted",
            "completed",
            "rejected",
            "canceled",
        ],
    )
    accepted_at: Optional[datetime] = Field(None, description="Acceptance timestamp")
    initiator_confirmed_at: Optional[datetime] = Field(
        None, description="Initiator confirmation timestamp"
    )
    responder_confirmed_at: Optional[datetime] = Field(
        None, description="Responder confirmation timestamp"
    )
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    canceled_at: Optional[datetime] = Field(
        None, description="Cancellation timestamp"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    items: Optional[List[TradeItemResponse]] = Field(
        None, description="Trade items (cards being exchanged)"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "423e4567-e89b-12d3-a456-426614174000",
                "initiator_id": "523e4567-e89b-12d3-a456-426614174000",
                "responder_id": "623e4567-e89b-12d3-a456-426614174000",
                "status": "proposed",
                "accepted_at": None,
                "initiator_confirmed_at": None,
                "responder_confirmed_at": None,
                "completed_at": None,
                "canceled_at": None,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "items": [
                    {
                        "id": "723e4567-e89b-12d3-a456-426614174000",
                        "trade_id": "423e4567-e89b-12d3-a456-426614174000",
                        "card_id": "123e4567-e89b-12d3-a456-426614174000",
                        "owner_side": "initiator",
                        "created_at": "2025-01-01T00:00:00Z",
                    }
                ],
            }
        }


class TradeHistoryResponse(BaseModel):
    """Response schema for trade history list"""

    trades: List[TradeResponse] = Field(..., description="List of trades")
    total: int = Field(..., description="Total number of trades")
    limit: int = Field(..., description="Limit used")
    offset: int = Field(..., description="Offset used")

    class Config:
        json_schema_extra = {
            "example": {
                "trades": [],
                "total": 5,
                "limit": 50,
                "offset": 0,
            }
        }
