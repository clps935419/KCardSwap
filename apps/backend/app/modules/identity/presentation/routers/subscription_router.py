"""
Subscription Router - API endpoints for subscription management
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.infrastructure.database.connection import get_db_session
from app.modules.identity.presentation.dependencies.auth_deps import get_current_user
from app.modules.identity.presentation.schemas.subscription_schemas import (
    VerifyReceiptRequest,
    SubscriptionStatusResponse,
    ExpireSubscriptionsResponse,
)
from app.modules.identity.application.use_cases.subscription.verify_receipt_use_case import VerifyReceiptUseCase
from app.modules.identity.application.use_cases.subscription.check_subscription_status_use_case import (
    CheckSubscriptionStatusUseCase,
)
from app.modules.identity.application.use_cases.subscription.expire_subscriptions_use_case import (
    ExpireSubscriptionsUseCase,
)
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
from app.modules.identity.infrastructure.repositories.purchase_token_repository_impl import (
    PurchaseTokenRepositoryImpl,
)
from app.modules.identity.infrastructure.external.google_play_billing_service import GooglePlayBillingService
from app.config import get_settings

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("/verify-receipt", response_model=SubscriptionStatusResponse)
async def verify_receipt(
    request: VerifyReceiptRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
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
    settings = get_settings()
    user_id = current_user["id"]
    
    # Initialize repositories
    subscription_repo = SubscriptionRepositoryImpl(session)
    token_repo = PurchaseTokenRepositoryImpl(session)
    
    # Initialize billing service
    billing_service = GooglePlayBillingService(
        package_name=settings.GOOGLE_PLAY_PACKAGE_NAME,
        service_account_key_path=settings.GOOGLE_PLAY_SERVICE_ACCOUNT_KEY_PATH,
    )
    
    # Execute use case
    use_case = VerifyReceiptUseCase(
        subscription_repository=subscription_repo,
        purchase_token_repository=token_repo,
        billing_service=billing_service,
    )
    
    result = await use_case.execute(
        user_id=user_id,
        platform=request.platform,
        purchase_token=request.purchase_token,
        product_id=request.product_id,
    )
    
    await session.commit()
    return result


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get current subscription status for authenticated user.
    
    Returns server-side subscription state.
    Called by app when opening or returning to foreground.
    
    Error codes:
    - 401_UNAUTHORIZED: Not logged in
    - 503_SERVICE_UNAVAILABLE: Database unavailable
    """
    user_id = current_user["id"]
    
    # Initialize repository
    subscription_repo = SubscriptionRepositoryImpl(session)
    
    # Execute use case
    use_case = CheckSubscriptionStatusUseCase(subscription_repo)
    result = await use_case.execute(user_id=user_id)
    
    await session.commit()
    return result


@router.post("/expire-subscriptions", response_model=ExpireSubscriptionsResponse)
async def expire_subscriptions(
    session: AsyncSession = Depends(get_db_session),
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
    # Initialize repository
    subscription_repo = SubscriptionRepositoryImpl(session)
    
    # Execute use case
    use_case = ExpireSubscriptionsUseCase(subscription_repo)
    result = await use_case.execute()
    
    await session.commit()
    return result
