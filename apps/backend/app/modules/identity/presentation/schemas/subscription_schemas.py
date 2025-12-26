"""
Subscription API Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VerifyReceiptRequest(BaseModel):
    """Request schema for verifying purchase receipt"""

    platform: str = Field(..., description="Platform: 'android' or 'ios'")
    purchase_token: str = Field(..., description="Purchase token from Google Play")
    product_id: str = Field(..., description="Product/SKU ID")

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "android",
                "purchase_token": "abc123xyz...",
                "product_id": "premium_monthly",
            }
        }


class SubscriptionStatusResponse(BaseModel):
    """Response schema for subscription status"""

    plan: str = Field(..., description="Subscription plan: 'free' or 'premium'")
    status: str = Field(
        ...,
        description="Subscription status: 'active', 'inactive', 'expired', 'pending'",
    )
    expires_at: Optional[str] = Field(None, description="Expiry datetime (ISO format)")
    entitlement_active: bool = Field(
        ..., description="Whether user has active premium entitlement"
    )
    source: str = Field(..., description="Subscription source: 'google_play'")

    class Config:
        json_schema_extra = {
            "example": {
                "plan": "premium",
                "status": "active",
                "expires_at": "2025-12-31T23:59:59",
                "entitlement_active": True,
                "source": "google_play",
            }
        }


class ExpireSubscriptionsResponse(BaseModel):
    """Response schema for expire subscriptions job"""

    expired_count: int = Field(..., description="Number of subscriptions expired")
    processed_at: str = Field(..., description="Processing timestamp (ISO format)")

    class Config:
        json_schema_extra = {
            "example": {"expired_count": 5, "processed_at": "2025-12-23T00:00:00"}
        }
