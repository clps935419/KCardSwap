"""
FCM Push Notification Service

Provides Firebase Cloud Messaging integration for sending push notifications to users.
"""

import logging
from typing import Dict, Optional

try:
    import firebase_admin
    from firebase_admin import credentials, messaging

    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

from app.config import config

logger = logging.getLogger(__name__)


class FCMService:
    """Firebase Cloud Messaging service for push notifications"""

    def __init__(self):
        self._initialized = False
        self._app = None

        if not FIREBASE_AVAILABLE:
            logger.warning(
                "firebase-admin SDK not installed. "
                "Push notifications will not be sent. "
                "Install with: pip install firebase-admin"
            )
            return

        # Initialize Firebase if credentials are provided
        if config.FCM_CREDENTIALS_PATH:
            try:
                cred = credentials.Certificate(config.FCM_CREDENTIALS_PATH)
                self._app = firebase_admin.initialize_app(cred)
                self._initialized = True
                logger.info("FCM service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize FCM service: {e}")
                self._initialized = False
        else:
            logger.warning(
                "FCM_CREDENTIALS_PATH not configured. "
                "Push notifications will not be sent."
            )

    async def send_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        fcm_token: Optional[str] = None,
    ) -> bool:
        """
        Send push notification to a user

        Args:
            user_id: User ID to send notification to
            title: Notification title
            body: Notification body text
            data: Optional custom data payload
            fcm_token: Optional FCM device token. If not provided, must be retrieved from user profile.

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not FIREBASE_AVAILABLE:
            logger.debug(
                f"Skipping notification to user {user_id}: firebase-admin not installed"
            )
            return False

        if not self._initialized:
            logger.debug(
                f"Skipping notification to user {user_id}: FCM not initialized"
            )
            return False

        if not fcm_token:
            # In a real implementation, we would fetch the FCM token from user profile
            # For now, we log and skip
            logger.warning(
                f"No FCM token provided for user {user_id}. "
                "Notification cannot be sent. "
                "Token should be retrieved from user profile."
            )
            return False

        try:
            # Build notification message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=fcm_token,
            )

            # Send message
            response = messaging.send(message)
            logger.info(
                f"Successfully sent notification to user {user_id}. "
                f"Message ID: {response}"
            )
            return True

        except messaging.UnregisteredError:
            logger.warning(
                f"FCM token for user {user_id} is invalid or unregistered. "
                "User should re-register their device."
            )
            return False

        except messaging.SenderIdMismatchError:
            logger.error(
                f"FCM token for user {user_id} belongs to a different Firebase project"
            )
            return False

        except Exception as e:
            logger.error(
                f"Failed to send notification to user {user_id}: {e}", exc_info=True
            )
            return False

    async def send_notification_to_multiple(
        self,
        user_tokens: Dict[str, str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, bool]:
        """
        Send push notification to multiple users

        Args:
            user_tokens: Dict mapping user_id to FCM token
            title: Notification title
            body: Notification body text
            data: Optional custom data payload

        Returns:
            Dict mapping user_id to success status
        """
        results = {}

        for user_id, fcm_token in user_tokens.items():
            success = await self.send_notification(
                user_id=user_id, title=title, body=body, data=data, fcm_token=fcm_token
            )
            results[user_id] = success

        return results


# Singleton instance
_fcm_service: Optional[FCMService] = None


def get_fcm_service() -> FCMService:
    """Get or create FCM service singleton"""
    global _fcm_service
    if _fcm_service is None:
        _fcm_service = FCMService()
    return _fcm_service
