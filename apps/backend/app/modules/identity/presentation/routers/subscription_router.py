"""
Subscription Router - API endpoints for subscription management
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.application.use_cases.subscription.check_subscription_status_use_case import (
    CheckSubscriptionStatusUseCase,
)
from app.modules.identity.application.use_cases.subscription.expire_subscriptions_use_case import (
    ExpireSubscriptionsUseCase,
)
from app.modules.identity.application.use_cases.subscription.verify_receipt_use_case import (
    VerifyReceiptUseCase,
)
from app.modules.identity.presentation.dependencies.use_case_deps import (
    get_check_subscription_status_use_case,
    get_expire_subscriptions_use_case,
    get_verify_receipt_use_case,
)
from app.modules.identity.presentation.schemas.subscription_schemas import (
    ExpireSubscriptionsData,
    ExpireSubscriptionsResponse,
    SubscriptionStatusData,
    SubscriptionStatusResponse,
    VerifyReceiptRequest,
)
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("/verify-receipt", response_model=SubscriptionStatusResponse)
async def verify_receipt(
    request: VerifyReceiptRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[VerifyReceiptUseCase, Depends(get_verify_receipt_use_case)],
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    Verify Google Play purchase receipt and update subscription.

    Features:
    - Idempotent: Same token + same user returns current status
    - Token binding: Prevents cross-user replay attacks
    - Auto-acknowledge: Acknowledges purchase after verification

    Error codes:
    - 400_VALIDATION_FAILED: Invalid platform or missing fields
    - 401_UNAUTHORIZED: Not logged in
    - 409_CONFLICT: Purchase token already used by another user
    - 503_SERVICE_UNAVAILABLE: Google Play API unavailable
    """
    # Execute use case
    result_dict = await use_case.execute(
        user_id=current_user_id,
        platform=request.platform,
        purchase_token=request.purchase_token,
        product_id=request.product_id,
    )

    await session.commit()

    # Wrap in envelope format
    data = SubscriptionStatusData(**result_dict)
    return SubscriptionStatusResponse(data=data, meta=None, error=None)


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[
        CheckSubscriptionStatusUseCase, Depends(get_check_subscription_status_use_case)
    ],
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    Get current subscription status for authenticated user.

    Returns server-side subscription state.
    Called by app when opening or returning to foreground.

    Error codes:
    - 401_UNAUTHORIZED: Not logged in
    - 503_SERVICE_UNAVAILABLE: Database unavailable
    """
    # Execute use case
    result_dict = await use_case.execute(user_id=current_user_id)

    await session.commit()

    # Wrap in envelope format
    data = SubscriptionStatusData(**result_dict)
    return SubscriptionStatusResponse(data=data, meta=None, error=None)


@router.post("/expire-subscriptions", response_model=ExpireSubscriptionsResponse)
async def expire_subscriptions(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    use_case: Annotated[
        ExpireSubscriptionsUseCase, Depends(get_expire_subscriptions_use_case)
    ],
):
    """
    Expire active subscriptions that have passed their expiry date.

    This endpoint should be called by a scheduled background task (e.g., daily cron job).
    For POC, it's exposed as an HTTP endpoint for manual triggering.

    In production, this should be:
    - Protected by admin authentication or internal-only access
    - Triggered by a scheduler (APScheduler, Celery Beat, Cloud Scheduler, etc.)

    Returns:
        Number of subscriptions expired and processing timestamp
    """
    # Execute use case
    result_dict = await use_case.execute()

    await session.commit()

    # Wrap in envelope format
    data = ExpireSubscriptionsData(**result_dict)
    return ExpireSubscriptionsResponse(data=data, meta=None, error=None)
