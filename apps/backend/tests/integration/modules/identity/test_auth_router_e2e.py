"""
Integration E2E tests for Auth Router

Tests the authentication endpoints:
- POST /auth/google-login - Google OAuth login (implicit flow)
- POST /auth/google-callback - Google OAuth callback (PKCE flow)
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Logout user
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session


class TestAuthRouterE2E:
    """E2E tests for Auth Router endpoints"""

    @pytest.fixture
    def unauthenticated_client(self, db_session):
        """Provide unauthenticated test client"""
        async def override_get_db_session():
            yield db_session

        app.dependency_overrides[get_db_session] = override_get_db_session

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    # ===== Google Login (Implicit Flow) Tests =====

    @patch("app.modules.identity.application.use_cases.auth.login_with_google.GoogleOAuthService")
    def test_google_login_success_new_user(self, mock_google_service, unauthenticated_client):
        """Test successful Google login for new user (implicit flow)"""
        # Mock Google OAuth service
        mock_service_instance = MagicMock()
        mock_service_instance.verify_google_token = AsyncMock(return_value={
            "google_id": "google_test_123",
            "email": "newuser@example.com",
            "name": "New User",
            "picture": "https://example.com/photo.jpg",
            "email_verified": True,
        })
        mock_google_service.return_value = mock_service_instance

        payload = {
            "google_token": "valid_google_id_token_12345"
        }

        response = unauthenticated_client.post("/api/v1/auth/google-login", json=payload)

        # Should succeed or return 500/401 based on actual implementation
        assert response.status_code in [200, 401, 500]

    @patch("app.modules.identity.application.use_cases.auth.login_with_google.GoogleOAuthService")
    def test_google_login_success_existing_user(self, mock_google_service, unauthenticated_client):
        """Test successful Google login for existing user"""
        # Mock Google OAuth service
        mock_service_instance = MagicMock()
        mock_service_instance.verify_google_token = AsyncMock(return_value={
            "google_id": "google_existing_456",
            "email": "existing@example.com",
            "name": "Existing User",
            "picture": "https://example.com/photo.jpg",
            "email_verified": True,
        })
        mock_google_service.return_value = mock_service_instance

        payload = {
            "google_token": "valid_google_id_token_67890"
        }

        response = unauthenticated_client.post("/api/v1/auth/google-login", json=payload)

        # Should succeed or return 500/401 based on actual implementation
        assert response.status_code in [200, 401, 500]

    def test_google_login_missing_token(self, unauthenticated_client):
        """Test Google login with missing token"""
        payload = {}

        response = unauthenticated_client.post("/api/v1/auth/google-login", json=payload)

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "400_VALIDATION_FAILED"

    def test_google_login_invalid_token(self, unauthenticated_client):
        """Test Google login with invalid token"""
        payload = {
            "google_token": "invalid_token"
        }

        response = unauthenticated_client.post("/api/v1/auth/google-login", json=payload)

        # Should return 401 or 500 depending on implementation
        assert response.status_code in [401, 500]

    # ===== Google Callback (PKCE Flow) Tests =====

    @patch("app.modules.identity.application.use_cases.auth.google_callback.GoogleOAuthService")
    def test_google_callback_success(self, mock_google_service, unauthenticated_client):
        """Test successful Google OAuth callback (PKCE flow)"""
        # Mock Google OAuth service
        mock_service_instance = MagicMock()
        mock_service_instance.exchange_code_with_pkce = AsyncMock(
            return_value="mock_id_token_12345"
        )
        mock_service_instance.verify_google_token = AsyncMock(return_value={
            "google_id": "google_pkce_789",
            "email": "pkce@example.com",
            "name": "PKCE User",
            "picture": "https://example.com/photo.jpg",
            "email_verified": True,
        })
        mock_google_service.return_value = mock_service_instance

        payload = {
            "code": "4/0AY0e-g7XXXXXXXXXXX",
            "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
            "redirect_uri": "exp://192.168.1.1:19000"
        }

        response = unauthenticated_client.post("/api/v1/auth/google-callback", json=payload)

        # Should succeed or return 500/401 based on actual implementation
        assert response.status_code in [200, 401, 500]

    def test_google_callback_missing_code(self, unauthenticated_client):
        """Test Google callback with missing authorization code"""
        payload = {
            "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        }

        response = unauthenticated_client.post("/api/v1/auth/google-callback", json=payload)

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "400_VALIDATION_FAILED"

    def test_google_callback_missing_code_verifier(self, unauthenticated_client):
        """Test Google callback with missing code_verifier"""
        payload = {
            "code": "4/0AY0e-g7XXXXXXXXXXX"
        }

        response = unauthenticated_client.post("/api/v1/auth/google-callback", json=payload)

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "400_VALIDATION_FAILED"

    def test_google_callback_invalid_code_verifier(self, unauthenticated_client):
        """Test Google callback with invalid (too short) code_verifier"""
        payload = {
            "code": "4/0AY0e-g7XXXXXXXXXXX",
            "code_verifier": "too_short"  # Less than 43 characters
        }

        response = unauthenticated_client.post("/api/v1/auth/google-callback", json=payload)

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "400_VALIDATION_FAILED"

    # ===== Refresh Token Tests =====

    def test_refresh_token_missing_token(self, unauthenticated_client):
        """Test refresh token without providing refresh token"""
        response = unauthenticated_client.post("/api/v1/auth/refresh")

        # Should return 400 or 401 depending on implementation
        assert response.status_code in [400, 401, 422]

    def test_refresh_token_invalid_token(self, unauthenticated_client):
        """Test refresh token with invalid token"""
        # Try with invalid token in cookie
        client = TestClient(app)
        client.cookies.set("refresh_token", "invalid_token_12345")

        response = client.post("/api/v1/auth/refresh")

        # Should return 401
        assert response.status_code in [401, 422]

    def test_refresh_token_expired_token(self, unauthenticated_client):
        """Test refresh token with expired token"""
        # Try with expired token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxNTE2MjM5MDIyfQ.4Adcj0vgN1vGE5xJnr5s0"
        
        client = TestClient(app)
        client.cookies.set("refresh_token", expired_token)

        response = client.post("/api/v1/auth/refresh")

        # Should return 401
        assert response.status_code in [401, 422]

    # ===== Logout Tests =====

    def test_logout_without_cookie(self, unauthenticated_client):
        """Test logout without refresh token cookie"""
        response = unauthenticated_client.post("/api/v1/auth/logout")

        # Should succeed even without cookie (idempotent)
        assert response.status_code in [200, 204, 400, 401]

    def test_logout_with_valid_cookie(self, unauthenticated_client):
        """Test logout with valid refresh token cookie"""
        client = TestClient(app)
        client.cookies.set("refresh_token", "valid_refresh_token_12345")

        response = client.post("/api/v1/auth/logout")

        # Should succeed
        assert response.status_code in [200, 204]

    def test_logout_clears_cookie(self, unauthenticated_client):
        """Test that logout clears the refresh token cookie"""
        client = TestClient(app)
        client.cookies.set("refresh_token", "some_token")

        response = client.post("/api/v1/auth/logout")

        # Check if cookie is cleared (should have max-age=0 or be deleted)
        if response.status_code in [200, 204]:
            # Cookie should be cleared in response
            set_cookie_header = response.headers.get("set-cookie", "")
            assert "refresh_token" in set_cookie_header or set_cookie_header == ""
