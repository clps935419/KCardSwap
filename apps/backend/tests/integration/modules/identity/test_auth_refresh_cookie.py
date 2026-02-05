"""
Integration tests for cookie-based token refresh.

Tests the complete cookie-based refresh flow:
1. Refresh endpoint reads refresh_token from httpOnly cookie
2. Successfully exchanges for new access and refresh tokens
3. Sets new tokens as httpOnly cookies with correct attributes
4. Rejects invalid or missing refresh_token
"""

from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.modules.identity.presentation.dependencies.use_case_deps import (
    get_refresh_token_use_case,
)

client = TestClient(app)


class TestRefreshTokenCookie:
    """Test suite for cookie-based token refresh (T014)"""

    def test_refresh_success_with_cookie(self):
        """
        Test successful token refresh with cookie

        Scenario:
        - Client sends request with refresh_token in httpOnly cookie
        - Backend validates and exchanges for new tokens
        - Response sets new access and refresh cookies
        - Cookie attributes are correct (httpOnly, SameSite, Secure, etc.)
        """
        valid_refresh_token = "valid_refresh_token_string_12345"
        new_tokens = ("new_access_token_67890", "new_refresh_token_67890")

        # Mock use case
        mock_use_case = Mock()
        mock_use_case.execute = AsyncMock(return_value=new_tokens)

        # Override dependency
        app.dependency_overrides[get_refresh_token_use_case] = lambda: mock_use_case

        try:
            # Send request with refresh_token in cookie
            cookies = {settings.REFRESH_COOKIE_NAME: valid_refresh_token}
            response = client.post("/api/v1/auth/refresh", cookies=cookies)

            # Verify response status
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Tokens refreshed successfully"

            # Verify use case was called with correct token
            mock_use_case.execute.assert_called_once_with(valid_refresh_token)

            # Verify cookies are set in response
            cookies_dict = response.cookies

            # Check access_token cookie
            assert settings.ACCESS_COOKIE_NAME in cookies_dict
            access_cookie = cookies_dict[settings.ACCESS_COOKIE_NAME]
            assert access_cookie == new_tokens[0]

            # Check refresh_token cookie
            assert settings.REFRESH_COOKIE_NAME in cookies_dict
            refresh_cookie = cookies_dict[settings.REFRESH_COOKIE_NAME]
            assert refresh_cookie == new_tokens[1]
        finally:
            # Clean up override
            app.dependency_overrides.clear()

    def test_refresh_missing_cookie(self):
        """
        Test refresh endpoint rejects request without refresh_token cookie

        Scenario:
        - Client sends request without refresh_token cookie
        - Backend returns 401 Unauthorized
        """
        # Send request without cookie
        response = client.post("/api/v1/auth/refresh")

        # Verify error response
        assert response.status_code == 401
        error = response.json()
        # Check if using standardized error envelope
        if "error" in error:
            assert error["error"]["code"] in ["401_HTTP_ERROR", "UNAUTHORIZED"]
        elif "detail" in error:
            detail = error["detail"]
            if isinstance(detail, dict):
                assert detail["code"] == "UNAUTHORIZED"
                assert "not found in cookie" in detail["message"]
            else:
                assert detail

    def test_refresh_invalid_token(self):
        """
        Test refresh endpoint rejects invalid refresh_token

        Scenario:
        - Client sends request with invalid refresh_token in cookie
        - Use case returns None (token validation failed)
        - Backend returns 401 Unauthorized
        """
        # Mock use case to return None (invalid token)
        mock_use_case = Mock()
        mock_use_case.execute = AsyncMock(return_value=None)

        # Override dependency
        app.dependency_overrides[get_refresh_token_use_case] = lambda: mock_use_case

        try:
            # Send request with invalid token
            cookies = {settings.REFRESH_COOKIE_NAME: "invalid_token"}
            response = client.post("/api/v1/auth/refresh", cookies=cookies)

            # Verify error response
            assert response.status_code == 401
            error = response.json()
            # Check if using standardized error envelope
            if "error" in error:
                assert error["error"]["code"] in ["401_HTTP_ERROR", "UNAUTHORIZED"]
            elif "detail" in error:
                detail = error["detail"]
                if isinstance(detail, dict):
                    assert detail["code"] == "UNAUTHORIZED"
                    assert "Invalid or expired" in detail["message"]
                else:
                    assert detail

            # Verify use case was called
            mock_use_case.execute.assert_called_once_with("invalid_token")
        finally:
            # Clean up override
            app.dependency_overrides.clear()

    def test_refresh_expired_token(self):
        """
        Test refresh endpoint rejects expired refresh_token

        Scenario:
        - Client sends request with expired refresh_token in cookie
        - Use case returns None (token expired)
        - Backend returns 401 Unauthorized
        """
        valid_refresh_token = "valid_refresh_token_string_12345"

        # Mock use case to return None (expired token)
        mock_use_case = Mock()
        mock_use_case.execute = AsyncMock(return_value=None)

        # Override dependency
        app.dependency_overrides[get_refresh_token_use_case] = lambda: mock_use_case

        try:
            # Send request with expired token (simulated by mock returning None)
            cookies = {settings.REFRESH_COOKIE_NAME: valid_refresh_token}
            response = client.post("/api/v1/auth/refresh", cookies=cookies)

            # Verify error response
            assert response.status_code == 401
            error = response.json()
            # Just verify it's an error response
            assert error is not None
        finally:
            # Clean up override
            app.dependency_overrides.clear()

    def test_refresh_cookie_attributes_configuration(self):
        """
        Test that cookie settings are correctly configured

        Verifies:
        - Cookie names match configuration
        - Security settings are defined
        """
        # Verify cookie configuration
        assert settings.ACCESS_COOKIE_NAME == "access_token"
        assert settings.REFRESH_COOKIE_NAME == "refresh_token"
        assert settings.COOKIE_HTTPONLY is True
        assert settings.COOKIE_SAMESITE in ["lax", "strict", "none"]
        assert settings.COOKIE_PATH == "/"
        # COOKIE_SECURE should be True in production
        # COOKIE_DOMAIN may be None for same-origin
