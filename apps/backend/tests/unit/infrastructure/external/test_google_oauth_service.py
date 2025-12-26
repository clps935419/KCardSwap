"""
Unit tests for GoogleOAuthService - PKCE flow
"""
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.modules.identity.infrastructure.external.google_oauth_service import (
    GoogleOAuthService,
)


class TestGoogleOAuthServicePKCE:
    """Test suite for GoogleOAuthService PKCE functionality"""

    @pytest.fixture
    def mock_env(self):
        """Mock environment variables"""
        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test_client_id",
                "GOOGLE_CLIENT_SECRET": "test_client_secret",
                "GOOGLE_REDIRECT_URI": "http://localhost:3000/callback",
            },
        ):
            yield

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_includes_client_secret(self, mock_env):
        """
        Test that exchange_code_with_pkce includes client_secret in the request

        This is critical: Even though PKCE is used (which protects against
        code interception on the client side), the backend still needs to
        send client_secret when it's a confidential client.

        PKCE protects the mobile app (no secret stored there), but the
        backend-to-Google communication should still use client_secret.
        """
        service = GoogleOAuthService()

        # Mock httpx.AsyncClient
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "mock_access_token",
            "id_token": "mock_id_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.exchange_code_with_pkce(
                code="test_authorization_code",
                code_verifier="test_code_verifier_must_be_43_to_128_chars_long_12345678",
                redirect_uri="http://localhost:3000/callback",
            )

            # Verify the result
            assert result == "mock_id_token"

            # Verify that post was called with correct parameters
            mock_client.__aenter__.return_value.post.assert_called_once()
            call_args = mock_client.__aenter__.return_value.post.call_args

            # Check the data payload
            data = call_args[1]["data"]
            assert data["code"] == "test_authorization_code"
            assert data["client_id"] == "test_client_id"
            assert (
                data["client_secret"] == "test_client_secret"
            )  # THIS IS THE KEY ASSERTION
            assert (
                data["code_verifier"]
                == "test_code_verifier_must_be_43_to_128_chars_long_12345678"
            )
            assert data["redirect_uri"] == "http://localhost:3000/callback"
            assert data["grant_type"] == "authorization_code"

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_uses_fallback_redirect_uri(self, mock_env):
        """
        Test that exchange_code_with_pkce uses configured redirect_uri when not provided
        """
        service = GoogleOAuthService()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id_token": "mock_id_token"}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.exchange_code_with_pkce(
                code="test_code",
                code_verifier="test_verifier_43_chars_minimum_required_1234567890",
                # No redirect_uri provided
            )

            assert result == "mock_id_token"

            # Verify fallback redirect_uri was used
            call_args = mock_client.__aenter__.return_value.post.call_args
            data = call_args[1]["data"]
            assert data["redirect_uri"] == "http://localhost:3000/callback"

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_handles_error_response(self, mock_env):
        """
        Test that exchange_code_with_pkce returns None on error response from Google
        """
        service = GoogleOAuthService()

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid authorization code",
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.exchange_code_with_pkce(
                code="invalid_code",
                code_verifier="test_verifier_43_chars_minimum_required_1234567890",
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_handles_timeout(self, mock_env):
        """
        Test that exchange_code_with_pkce handles timeout gracefully
        """
        service = GoogleOAuthService()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("Timeout")
        )

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.exchange_code_with_pkce(
                code="test_code",
                code_verifier="test_verifier_43_chars_minimum_required_1234567890",
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce_vs_regular_exchange(self, mock_env):
        """
        Test that both PKCE and regular code exchange include client_secret

        This documents that:
        - Regular flow: Uses client_secret (web apps)
        - PKCE flow: Also uses client_secret on backend (mobile apps)

        The difference is that PKCE adds code_verifier for additional security,
        but doesn't replace client_secret on the backend.
        """
        service = GoogleOAuthService()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id_token": "mock_id_token"}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            # Test regular exchange
            await service.exchange_code_for_token(code="test_code")
            regular_call_args = mock_client.__aenter__.return_value.post.call_args
            regular_data = regular_call_args[1]["data"]

            # Reset mock
            mock_client.__aenter__.return_value.post.reset_mock()

            # Test PKCE exchange
            await service.exchange_code_with_pkce(
                code="test_code",
                code_verifier="test_verifier_43_chars_minimum_required_1234567890",
            )
            pkce_call_args = mock_client.__aenter__.return_value.post.call_args
            pkce_data = pkce_call_args[1]["data"]

            # Both should include client_secret
            assert "client_secret" in regular_data
            assert "client_secret" in pkce_data
            assert regular_data["client_secret"] == pkce_data["client_secret"]

            # PKCE should have code_verifier, regular should not
            assert "code_verifier" not in regular_data
            assert "code_verifier" in pkce_data
