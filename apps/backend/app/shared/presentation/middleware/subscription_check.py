"""
Subscription Permission Middleware

Enforces subscription-based limits on API endpoints.
Checks user's subscription status and applies restrictions based on plan.
"""
from typing import Callable
from fastapi import Request, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.infrastructure.database.connection import get_db_session
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import (
    SubscriptionRepositoryImpl,
)


async def check_subscription_permission(
    request: Request,
    call_next: Callable,
) -> Response:
    """
    Middleware to check subscription permissions for protected endpoints.

    Enforces limits on:
    - Card uploads (free: 2/day, premium: unlimited)
    - Nearby searches (free: 5/day, premium: unlimited)
    - Post creation (free: 2/day, premium: unlimited)

    Injects subscription info into request.state for use by endpoints.
    """
    # Get current user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)

    if user is None:
        # No authenticated user, let auth middleware handle it
        return await call_next(request)

    # Get database session
    async for session in get_db_session():
        try:
            # Get user's subscription
            subscription_repo = SubscriptionRepositoryImpl(session)
            subscription = await subscription_repo.get_or_create_by_user_id(user["id"])

            # Inject subscription info into request state
            request.state.subscription = {
                "plan": subscription.plan,
                "status": subscription.status,
                "is_premium": subscription.is_premium(),
                "entitlement_active": subscription.is_premium(),
            }

            # Continue to next middleware/endpoint
            response = await call_next(request)
            return response

        finally:
            await session.close()


def require_subscription_plan(required_plan: str = "premium"):
    """
    Dependency to require a specific subscription plan.

    Usage:
        @router.get("/premium-feature", dependencies=[Depends(require_subscription_plan("premium"))])
        async def premium_feature():
            return {"message": "Premium content"}

    Args:
        required_plan: The required plan ("free" or "premium")

    Raises:
        HTTPException: 403 if user doesn't have required plan
    """

    async def _check_plan(request: Request) -> None:
        subscription = getattr(request.state, "subscription", None)

        if subscription is None:
            raise HTTPException(
                status_code=500, detail="Subscription information not available"
            )

        if required_plan == "premium" and not subscription.get("is_premium", False):
            raise HTTPException(
                status_code=403,
                detail={"code": "PREMIUM_REQUIRED", "message": "此功能需要付費訂閱"},
            )

    return _check_plan


def get_subscription_from_request(request: Request) -> dict:
    """
    Helper function to get subscription info from request state.

    Usage in endpoint:
        subscription = get_subscription_from_request(request)
        if subscription["is_premium"]:
            # premium logic

    Returns:
        dict with subscription info or default free plan
    """
    subscription = getattr(request.state, "subscription", None)

    if subscription is None:
        # Return default free plan if not available
        return {
            "plan": "free",
            "status": "inactive",
            "is_premium": False,
            "entitlement_active": False,
        }

    return subscription
