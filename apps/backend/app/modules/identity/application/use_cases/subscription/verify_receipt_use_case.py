"""
Verify Receipt Use Case - Verify Google Play purchase and update subscription
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.modules.identity.domain.repositories.subscription_repository import SubscriptionRepository
from app.modules.identity.domain.repositories.purchase_token_repository import PurchaseTokenRepository
from app.modules.identity.infrastructure.external.google_play_billing_service import GooglePlayBillingService
from app.shared.presentation.exceptions.api_exceptions import (
    ValidationException,
    ConflictException,
    ServiceUnavailableException,
)

logger = logging.getLogger(__name__)


class VerifyReceiptUseCase:
    """
    Use case for verifying Google Play purchase receipts.
    
    Features:
    - Idempotent: Same token + same user returns current status
    - Token binding: Prevents cross-user replay attacks
    - Auto-acknowledge: Acknowledges purchase after successful verification
    """
    
    def __init__(
        self,
        subscription_repository: SubscriptionRepository,
        purchase_token_repository: PurchaseTokenRepository,
        billing_service: GooglePlayBillingService,
    ):
        self.subscription_repo = subscription_repository
        self.token_repo = purchase_token_repository
        self.billing_service = billing_service
    
    async def execute(
        self,
        user_id: UUID,
        platform: str,
        purchase_token: str,
        product_id: str,
    ) -> dict:
        """
        Verify purchase receipt and update subscription.
        
        Args:
            user_id: The user making the purchase
            platform: "android" or "ios"
            purchase_token: Purchase token from Google Play
            product_id: Product/SKU ID
        
        Returns:
            dict with:
            - plan: "free" or "premium"
            - status: "active", "inactive", "expired", "pending"
            - expires_at: datetime or None
            - entitlement_active: bool
            - source: "google_play"
        
        Raises:
            ValidationException: Invalid input
            ConflictException: Token already used by another user
            ServiceUnavailableException: Google Play API unavailable
        """
        # Validate platform
        if platform not in ["android", "ios"]:
            raise ValidationException(
                "UNSUPPORTED_PLATFORM",
                f"平台 '{platform}' 不支援"
            )
        
        # Currently only support Android
        if platform != "android":
            raise ValidationException(
                "UNSUPPORTED_PLATFORM",
                "目前僅支援 Android 平台"
            )
        
        # Check if token is already bound to a different user
        existing_user_id = await self.token_repo.get_user_id_for_token(purchase_token)
        if existing_user_id is not None and existing_user_id != user_id:
            raise ConflictException(
                "PURCHASE_TOKEN_ALREADY_USED",
                "此購買已被其他帳號使用"
            )
        
        # If token is already bound to this user, return current subscription status (idempotent)
        if existing_user_id == user_id:
            subscription = await self.subscription_repo.get_or_create_by_user_id(user_id)
            return self._build_response(subscription)
        
        # Verify purchase with Google Play
        try:
            verification = await self.billing_service.verify_subscription_purchase(
                product_id=product_id,
                purchase_token=purchase_token,
            )
        except Exception as e:
            logger.error(f"Failed to verify purchase: {str(e)}")
            raise ServiceUnavailableException(
                "GOOGLE_PLAY_UNAVAILABLE",
                "驗證暫時失敗，請稍後再試"
            )
        
        # Get or create subscription
        subscription = await self.subscription_repo.get_or_create_by_user_id(user_id)
        
        # Update subscription based on verification result
        if verification["is_valid"]:
            # Activate premium subscription
            subscription.activate(expires_at=verification["expires_at"])
            subscription = await self.subscription_repo.update(subscription)
            
            # Bind token to user (prevents replay)
            await self.token_repo.bind_token_to_user(
                purchase_token=purchase_token,
                user_id=user_id,
                product_id=product_id,
                platform=platform,
            )
            
            # Acknowledge purchase with Google Play (idempotent)
            try:
                await self.billing_service.acknowledge_subscription_purchase(
                    product_id=product_id,
                    purchase_token=purchase_token,
                )
            except Exception as e:
                logger.error(f"Failed to acknowledge purchase: {str(e)}")
                # Don't fail the request if acknowledgement fails
                # The subscription is already activated
        else:
            # Handle different payment states
            payment_state = verification.get("payment_state", 0)
            
            if payment_state == 0:  # Pending
                subscription.status = "pending"
                subscription.updated_at = datetime.utcnow()
                await self.subscription_repo.update(subscription)
            else:
                # Invalid or expired purchase
                if subscription.status == "active":
                    subscription.mark_as_expired()
                    await self.subscription_repo.update(subscription)
        
        return self._build_response(subscription)
    
    def _build_response(self, subscription) -> dict:
        """Build standardized response"""
        entitlement_active = subscription.is_premium()
        
        return {
            "plan": subscription.plan,
            "status": subscription.status,
            "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
            "entitlement_active": entitlement_active,
            "source": "google_play",
        }
