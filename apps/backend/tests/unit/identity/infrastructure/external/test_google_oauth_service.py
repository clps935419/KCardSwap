"""
Unit tests for GoogleOAuthService

Tests the Google OAuth service implementation with mocked HTTP clients
and Google auth library.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.modules.identity.infrastructure.external.google_oauth_service import (
    GoogleOAuthService,
)


class TestGoogleOAuthService:
    """Test GoogleOAuthService"""

    @pytest.fixture
    def service(self):
        """Create GoogleOAuthService instance"""
        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-client-id",
                "GOOGLE_CLIENT_SECRET": "test-client-secret",
                "GOOGLE_REDIRECT_URI": "http://localhost:8000/callback",
            },
        ):
            return GoogleOAuthService()

    @pytest.fixture
    def valid_token_info(self):
        """Create valid token info"""
        return {
            "iss": "accounts.google.com",
            "sub": "google-user-123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/photo.jpg",
            "email_verified": True,
        }

    # Tests for verify_google_token
    @pytest.mark.asyncio
    async def test_verify_google_token_success(self, service, valid_token_info):
        """Test successful token verification"""
        # Arrange
        with patch(
            "app.modules.identity.infrastructure.external.google_oauth_service.id_token.verify_oauth2_token"
        ) as mock_verify:
            mock_verify.return_value = valid_token_info

            # Act
            result = await service.verify_google_token("valid-token")

            # Assert
            assert result is not None
            assert result["google_id"] == "google-user-123"
            assert result["email"] == "test@example.com"
            assert result["name"] == "Test User"
            assert result["picture"] == "https://example.com/photo.jpg"
            assert result["email_verified"] is True
            mock_verify.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_google_token_invalid_issuer(self, service):
        """Test token verification with invalid issuer"""
        # Arrange
        invalid_token_info = {
            "iss": "malicious.com",  # Invalid issuer
            "sub": "user-123",
            "email": "test@example.com",
        }

        with patch(
            "app.modules.identity.infrastructure.external.google_oauth_service.id_token.verify_oauth2_token"
        ) as mock_verify:
            mock_verify.return_value = invalid_token_info

            # Act
            result = await service.verify_google_token("token-with-bad-issuer")

            # Assert
            assert result is None

    @pytest.mark.asyncio
    async def test_verify_google_token_value_error(self, service):
        """Test token verification with ValueError (invalid token)"""
        # Arrange
        with patch(
            "app.modules.identity.infrastructure.external.google_oauth_service.id_token.verify_oauth2_token"
        ) as mock_verify:
            mock_verify.side_effect = ValueError("Invalid token")

            # Act
            result = await service.verify_google_token("invalid-token")

            # Assert
            assert result is None

    @pytest.mark.asyncio
    async def test_verify_google_token_https_issuer(self, service, valid_token_info):
        """Test token verification with HTTPS issuer URL"""
        # Arrange
        valid_token_info["iss"] = "https://accounts.google.com"

        with patch(
            "app.modules.identity.infrastructure.external.google_oauth_service.id_token.verify_oauth2_token"
        ) as mock_verify:
            mock_verify.return_value = valid_token_info

            # Act
            result = await service.verify_google_token("valid-token")

            # Assert
            assert result is not None
            assert result["google_id"] == "google-user-123"

    # Tests for exchange_code_for_token
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, service):
        """Test successful code exchange"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id_token": "test-id-token",
            "access_token": "test-access-token",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Act
            result = await service.exchange_code_for_token("auth-code-123")

            # Assert
            assert result == "test-id-token"
            mock_client_instance.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_failure(self, service):
        """Test code exchange with non-200 status"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_grant"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Act
            result = await service.exchange_code_for_token("invalid-code")

            # Assert
            assert result is None

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_exception(self, service):
        """Test code exchange with network exception"""
        # Arrange
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(
                side_effect=Exception("Network error")
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Act
            result = await service.exchange_code_for_token("auth-code-123")

            # Assert
            assert result is None

    # Tests for exchange_code_with_pkce
    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_success(self, service):
        """Test successful PKCE code exchange"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id_token": "test-id-token-pkce",
            "access_token": "test-access-token",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Act
            result = await service.exchange_code_with_pkce(
                "auth-code-123", "test-code-verifier-with-43-chars-minimum-len"
            )

            # Assert
            assert result == "test-id-token-pkce"
            mock_client_instance.post.assert_called_once()
            # Verify the request includes code_verifier
            call_args = mock_client_instance.post.call_args
            assert "data" in call_args.kwargs
            assert call_args.kwargs["data"]["code_verifier"] == "test-code-verifier-with-43-chars-minimum-len"

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_custom_redirect_uri(self, service):
        """Test PKCE exchange with custom redirect URI"""
        # Arrange
        custom_redirect = "exp://192.168.1.1:8081"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id_token": "test-token"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Act
            result = await service.exchange_code_with_pkce(
                "code", "verifier-12345678901234567890123456789012", custom_redirect
            )

            # Assert
            assert result == "test-token"
            call_args = mock_client_instance.post.call_args
            assert call_args.kwargs["data"]["redirect_uri"] == custom_redirect

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_failure(self, service):
        """Test PKCE exchange with non-200 status"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "invalid_grant"}'

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Act
            result = await service.exchange_code_with_pkce(
                "invalid-code", "verifier-12345678901234567890123456789012"
            )

            # Assert
            assert result is None

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_timeout(self, service):
        """Test PKCE exchange with timeout exception"""
        # Arrange
        import httpx

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout")
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Act
            result = await service.exchange_code_with_pkce(
                "code", "verifier-12345678901234567890123456789012"
            )

            # Assert
            assert result is None

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_general_exception(self, service):
        """Test PKCE exchange with general exception"""
        # Arrange
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(
                side_effect=Exception("Unexpected error")
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Act
            result = await service.exchange_code_with_pkce(
                "code", "verifier-12345678901234567890123456789012"
            )

            # Assert
            assert result is None
