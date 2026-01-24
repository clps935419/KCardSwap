"""
Unit tests for FCMService

Tests the Firebase Cloud Messaging service implementation with mocked
Firebase Admin SDK.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.shared.infrastructure.external.fcm_service import FCMService


class TestFCMService:
    """Test FCMService"""

    @pytest.fixture
    def mock_credentials_path(self, tmp_path):
        """Create temporary credentials file"""
        creds_file = tmp_path / "firebase-credentials.json"
        creds_file.write_text('{"type": "service_account", "project_id": "test"}')
        return str(creds_file)

    # Test initialization
    def test_init_without_firebase_available(self):
        """Test initialization when firebase-admin is not available"""
        # Arrange & Act
        with patch(
            "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE", False
        ):
            service = FCMService()

            # Assert
            assert service._initialized is False
            assert service._app is None

    def test_init_with_credentials(self, mock_credentials_path):
        """Test initialization with valid credentials"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch(
                "app.shared.infrastructure.external.fcm_service.credentials"
            ) as mock_creds,
            patch(
                "app.shared.infrastructure.external.fcm_service.firebase_admin"
            ) as mock_firebase,
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            mock_app = MagicMock()
            mock_firebase.initialize_app.return_value = mock_app

            # Act
            service = FCMService()

            # Assert
            assert service._initialized is True
            assert service._app == mock_app
            mock_creds.Certificate.assert_called_once_with(mock_credentials_path)
            mock_firebase.initialize_app.assert_called_once()

    def test_init_without_credentials_path(self):
        """Test initialization without FCM_CREDENTIALS_PATH configured"""
        # Arrange & Act
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
        ):
            mock_config.FCM_CREDENTIALS_PATH = None

            service = FCMService()

            # Assert
            assert service._initialized is False

    def test_init_with_invalid_credentials(self, tmp_path):
        """Test initialization with invalid credentials file"""
        # Arrange
        invalid_creds = tmp_path / "invalid.json"
        invalid_creds.write_text("invalid json")

        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch(
                "app.shared.infrastructure.external.fcm_service.credentials"
            ) as mock_creds,
        ):
            mock_config.FCM_CREDENTIALS_PATH = str(invalid_creds)
            mock_creds.Certificate.side_effect = Exception("Invalid credentials")

            # Act
            service = FCMService()

            # Assert
            assert service._initialized is False

    # Tests for send_notification
    @pytest.mark.asyncio
    async def test_send_notification_firebase_not_available(self):
        """Test send_notification when firebase-admin is not available"""
        # Arrange
        with patch(
            "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE", False
        ):
            service = FCMService()

            # Act
            result = await service.send_notification(
                user_id="user-123",
                title="Test",
                body="Message",
                fcm_token="token-123",
            )

            # Assert
            assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_not_initialized(self):
        """Test send_notification when service is not initialized"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
        ):
            mock_config.FCM_CREDENTIALS_PATH = None
            service = FCMService()

            # Act
            result = await service.send_notification(
                user_id="user-123",
                title="Test",
                body="Message",
                fcm_token="token-123",
            )

            # Assert
            assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_no_token(self, mock_credentials_path):
        """Test send_notification without FCM token"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch("app.shared.infrastructure.external.fcm_service.credentials"),
            patch("app.shared.infrastructure.external.fcm_service.firebase_admin"),
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            service = FCMService()

            # Act
            result = await service.send_notification(
                user_id="user-123",
                title="Test",
                body="Message",
                fcm_token=None,
            )

            # Assert
            assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_success(self, mock_credentials_path):
        """Test successful notification send"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch("app.shared.infrastructure.external.fcm_service.credentials"),
            patch("app.shared.infrastructure.external.fcm_service.firebase_admin"),
            patch(
                "app.shared.infrastructure.external.fcm_service.messaging"
            ) as mock_messaging,
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            # Mock exception classes as proper exceptions
            mock_messaging.UnregisteredError = type(
                "UnregisteredError", (Exception,), {}
            )
            mock_messaging.SenderIdMismatchError = type(
                "SenderIdMismatchError", (Exception,), {}
            )
            mock_messaging.send.return_value = "message-id-123"
            service = FCMService()

            # Act
            result = await service.send_notification(
                user_id="user-123",
                title="Test Title",
                body="Test Body",
                data={"type": "chat", "room_id": "room-1"},
                fcm_token="valid-token-123",
            )

            # Assert
            assert result is True
            mock_messaging.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_unregistered_error(self, mock_credentials_path):
        """Test notification send with unregistered token"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch("app.shared.infrastructure.external.fcm_service.credentials"),
            patch("app.shared.infrastructure.external.fcm_service.firebase_admin"),
            patch(
                "app.shared.infrastructure.external.fcm_service.messaging"
            ) as mock_messaging,
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            # Create exception classes first
            UnregisteredError = type("UnregisteredError", (Exception,), {})
            SenderIdMismatchError = type("SenderIdMismatchError", (Exception,), {})
            mock_messaging.UnregisteredError = UnregisteredError
            mock_messaging.SenderIdMismatchError = SenderIdMismatchError
            
            mock_messaging.send.side_effect = UnregisteredError(
                "Token is unregistered"
            )
            service = FCMService()

            # Act
            result = await service.send_notification(
                user_id="user-123",
                title="Test",
                body="Message",
                fcm_token="unregistered-token",
            )

            # Assert
            assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_sender_id_mismatch_error(
        self, mock_credentials_path
    ):
        """Test notification send with sender ID mismatch"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch("app.shared.infrastructure.external.fcm_service.credentials"),
            patch("app.shared.infrastructure.external.fcm_service.firebase_admin"),
            patch(
                "app.shared.infrastructure.external.fcm_service.messaging"
            ) as mock_messaging,
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            # Create exception classes first
            UnregisteredError = type("UnregisteredError", (Exception,), {})
            SenderIdMismatchError = type("SenderIdMismatchError", (Exception,), {})
            mock_messaging.UnregisteredError = UnregisteredError
            mock_messaging.SenderIdMismatchError = SenderIdMismatchError
            
            mock_messaging.send.side_effect = SenderIdMismatchError(
                "Sender ID mismatch"
            )
            service = FCMService()

            # Act
            result = await service.send_notification(
                user_id="user-123",
                title="Test",
                body="Message",
                fcm_token="wrong-project-token",
            )

            # Assert
            assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_general_exception(self, mock_credentials_path):
        """Test notification send with general exception"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch("app.shared.infrastructure.external.fcm_service.credentials"),
            patch("app.shared.infrastructure.external.fcm_service.firebase_admin"),
            patch(
                "app.shared.infrastructure.external.fcm_service.messaging"
            ) as mock_messaging,
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            # Create exception classes first
            mock_messaging.UnregisteredError = type("UnregisteredError", (Exception,), {})
            mock_messaging.SenderIdMismatchError = type("SenderIdMismatchError", (Exception,), {})
            mock_messaging.send.side_effect = Exception("Unexpected error")
            service = FCMService()

            # Act
            result = await service.send_notification(
                user_id="user-123",
                title="Test",
                body="Message",
                fcm_token="token-123",
            )

            # Assert
            assert result is False

    # Tests for send_notification_to_multiple
    @pytest.mark.asyncio
    async def test_send_notification_to_multiple_success(self, mock_credentials_path):
        """Test sending notifications to multiple users"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch("app.shared.infrastructure.external.fcm_service.credentials"),
            patch("app.shared.infrastructure.external.fcm_service.firebase_admin"),
            patch(
                "app.shared.infrastructure.external.fcm_service.messaging"
            ) as mock_messaging,
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            # Create exception classes first
            mock_messaging.UnregisteredError = type("UnregisteredError", (Exception,), {})
            mock_messaging.SenderIdMismatchError = type("SenderIdMismatchError", (Exception,), {})
            mock_messaging.send.return_value = "message-id"
            service = FCMService()

            user_tokens = {
                "user-1": "token-1",
                "user-2": "token-2",
                "user-3": "token-3",
            }

            # Act
            results = await service.send_notification_to_multiple(
                user_tokens=user_tokens,
                title="Broadcast Title",
                body="Broadcast Body",
                data={"type": "announcement"},
            )

            # Assert
            assert len(results) == 3
            assert results["user-1"] is True
            assert results["user-2"] is True
            assert results["user-3"] is True
            assert mock_messaging.send.call_count == 3

    @pytest.mark.asyncio
    async def test_send_notification_to_multiple_partial_failure(
        self, mock_credentials_path
    ):
        """Test sending notifications with some failures"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch("app.shared.infrastructure.external.fcm_service.credentials"),
            patch("app.shared.infrastructure.external.fcm_service.firebase_admin"),
            patch(
                "app.shared.infrastructure.external.fcm_service.messaging"
            ) as mock_messaging,
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            # Create exception classes first
            mock_messaging.UnregisteredError = type("UnregisteredError", (Exception,), {})
            mock_messaging.SenderIdMismatchError = type("SenderIdMismatchError", (Exception,), {})

            # First call succeeds, second fails, third succeeds
            mock_messaging.send.side_effect = [
                "message-id-1",
                Exception("Send failed"),
                "message-id-3",
            ]
            service = FCMService()

            user_tokens = {
                "user-1": "token-1",
                "user-2": "invalid-token",
                "user-3": "token-3",
            }

            # Act
            results = await service.send_notification_to_multiple(
                user_tokens=user_tokens, title="Test", body="Message"
            )

            # Assert
            assert len(results) == 3
            assert results["user-1"] is True
            assert results["user-2"] is False
            assert results["user-3"] is True

    @pytest.mark.asyncio
    async def test_send_notification_to_multiple_empty_list(self, mock_credentials_path):
        """Test sending notifications to empty list"""
        # Arrange
        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
            patch("app.shared.infrastructure.external.fcm_service.credentials"),
            patch("app.shared.infrastructure.external.fcm_service.firebase_admin"),
        ):
            mock_config.FCM_CREDENTIALS_PATH = mock_credentials_path
            service = FCMService()

            # Act
            results = await service.send_notification_to_multiple(
                user_tokens={}, title="Test", body="Message"
            )

            # Assert
            assert results == {}

    # Test get_fcm_service singleton
    def test_get_fcm_service_singleton(self):
        """Test get_fcm_service returns singleton"""
        # Arrange
        from app.shared.infrastructure.external.fcm_service import get_fcm_service

        with (
            patch(
                "app.shared.infrastructure.external.fcm_service.FIREBASE_AVAILABLE",
                True,
            ),
            patch("app.shared.infrastructure.external.fcm_service.config") as mock_config,
        ):
            mock_config.FCM_CREDENTIALS_PATH = None

            # Reset singleton
            import app.shared.infrastructure.external.fcm_service as fcm_module

            fcm_module._fcm_service = None

            # Act
            service1 = get_fcm_service()
            service2 = get_fcm_service()

            # Assert
            assert service1 is service2
