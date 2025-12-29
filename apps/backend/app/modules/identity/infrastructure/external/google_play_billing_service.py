"""
Google Play Billing Service - For verifying and acknowledging purchase receipts
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from google.auth.transport.requests import Request
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class GooglePlayBillingService:
    """
    Service for verifying Google Play purchase receipts and acknowledging purchases.

    Uses Google Play Developer API v3.
    """

    def __init__(
        self,
        package_name: str,
        service_account_key_path: Optional[str] = None,
        service_account_key_json: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Google Play Billing Service.

        Args:
            package_name: Android app package name
            service_account_key_path: Path to service account JSON key file
            service_account_key_json: Service account JSON key as dict
        """
        self.package_name = package_name
        self.base_url = "https://androidpublisher.googleapis.com/androidpublisher/v3"

        # Initialize credentials
        if service_account_key_json:
            self.credentials = service_account.Credentials.from_service_account_info(
                service_account_key_json,
                scopes=["https://www.googleapis.com/auth/androidpublisher"],
            )
        elif service_account_key_path:
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_key_path,
                scopes=["https://www.googleapis.com/auth/androidpublisher"],
            )
        else:
            raise ValueError(
                "Either service_account_key_path or service_account_key_json must be provided"
            )

    def _get_access_token(self) -> str:
        """Get fresh access token from service account"""
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return self.credentials.token

    async def verify_subscription_purchase(
        self,
        product_id: str,
        purchase_token: str,
    ) -> Dict[str, Any]:
        """
        Verify a subscription purchase with Google Play.

        Args:
            product_id: The subscription product ID
            purchase_token: The purchase token from Google Play

        Returns:
            Dict containing subscription details:
            - is_valid: bool
            - expires_at: datetime or None
            - auto_renewing: bool
            - payment_state: int (0=pending, 1=received, 2=free_trial, 3=pending_deferred)
            - acknowledgement_state: int (0=yet_to_be_acknowledged, 1=acknowledged)

        Raises:
            httpx.HTTPError: If API call fails
        """
        url = (
            f"{self.base_url}/applications/{self.package_name}"
            f"/purchases/subscriptions/{product_id}/tokens/{purchase_token}"
        )

        access_token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                # Parse response
                expires_timestamp_ms = data.get("expiryTimeMillis")
                expires_at = None
                if expires_timestamp_ms:
                    expires_at = datetime.fromtimestamp(
                        int(expires_timestamp_ms) / 1000
                    )

                payment_state = data.get("paymentState", 0)
                acknowledgement_state = data.get("acknowledgementState", 0)

                # Subscription is valid if payment is received and not expired
                is_valid = (
                    payment_state == 1  # Payment received
                    and expires_at is not None
                    and datetime.utcnow() < expires_at
                )

                return {
                    "is_valid": is_valid,
                    "expires_at": expires_at,
                    "auto_renewing": data.get("autoRenewing", False),
                    "payment_state": payment_state,
                    "acknowledgement_state": acknowledgement_state,
                    "raw_response": data,
                }

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.warning(
                        f"Purchase token not found: {purchase_token[:20]}..."
                    )
                    return {
                        "is_valid": False,
                        "expires_at": None,
                        "auto_renewing": False,
                        "payment_state": 0,
                        "acknowledgement_state": 0,
                        "error": "Purchase not found",
                    }
                else:
                    logger.error(
                        f"Google Play API error: {e.response.status_code} - {e.response.text}"
                    )
                    raise

            except Exception as e:
                logger.error(f"Error verifying purchase: {str(e)}")
                raise

    async def acknowledge_subscription_purchase(
        self,
        product_id: str,
        purchase_token: str,
    ) -> bool:
        """
        Acknowledge a subscription purchase with Google Play.
        Must be called after verifying the purchase to prevent refunds.

        Args:
            product_id: The subscription product ID
            purchase_token: The purchase token from Google Play

        Returns:
            True if acknowledged successfully (or already acknowledged)

        Raises:
            httpx.HTTPError: If API call fails
        """
        # First check if already acknowledged
        verification = await self.verify_subscription_purchase(
            product_id, purchase_token
        )
        if verification.get("acknowledgement_state") == 1:
            logger.info(f"Purchase already acknowledged: {purchase_token[:20]}...")
            return True

        url = (
            f"{self.base_url}/applications/{self.package_name}"
            f"/purchases/subscriptions/{product_id}/tokens/{purchase_token}:acknowledge"
        )

        access_token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                logger.info(f"Purchase acknowledged: {purchase_token[:20]}...")
                return True

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    # May already be acknowledged
                    logger.warning(
                        f"Purchase may already be acknowledged: {purchase_token[:20]}..."
                    )
                    return True
                else:
                    logger.error(
                        f"Google Play API error: {e.response.status_code} - {e.response.text}"
                    )
                    raise

            except Exception as e:
                logger.error(f"Error acknowledging purchase: {str(e)}")
                raise
