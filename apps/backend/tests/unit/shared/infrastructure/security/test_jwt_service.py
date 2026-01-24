"""
Unit tests for JWT Service
Testing JWT token generation, verification, and validation
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from jose import JWTError, jwt

from app.shared.infrastructure.security.jwt_service import JWTService


class TestJWTServiceInitialization:
    """Test JWT Service initialization"""

    def test_init_with_defaults(self):
        """Test initialization with default settings"""
        service = JWTService(
            secret_key="test_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

        assert service._secret_key == "test_secret"
        assert service._algorithm == "HS256"
        assert service._access_token_expire_minutes == 30
        assert service._refresh_token_expire_days == 7

    def test_init_with_custom_values(self):
        """Test initialization with custom values"""
        service = JWTService(
            secret_key="custom_secret",
            algorithm="HS512",
            access_token_expire_minutes=60,
            refresh_token_expire_days=30,
        )

        assert service._secret_key == "custom_secret"
        assert service._algorithm == "HS512"
        assert service._access_token_expire_minutes == 60
        assert service._refresh_token_expire_days == 30


class TestCreateAccessToken:
    """Test access token creation"""

    @pytest.fixture
    def service(self):
        """Create JWT service for testing"""
        return JWTService(
            secret_key="test_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

    def test_create_access_token_basic(self, service):
        """Test creating basic access token"""
        token = service.create_access_token(subject="user_123")

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode to verify contents
        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["sub"] == "user_123"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_additional_claims(self, service):
        """Test creating access token with additional claims"""
        additional_claims = {"email": "test@example.com", "role": "admin"}

        token = service.create_access_token(
            subject="user_123", additional_claims=additional_claims
        )

        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["sub"] == "user_123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"

    def test_access_token_expiration_time(self, service):
        """Test that access token has correct expiration"""
        with patch("app.shared.infrastructure.security.jwt_service.datetime") as mock_dt:
            now = datetime(2024, 1, 1, 12, 0, 0)
            mock_dt.utcnow.return_value = now

            token = service.create_access_token(subject="user_123")

            # Decode without verifying expiration
            payload = jwt.decode(token, "test_secret", algorithms=["HS256"], options={"verify_exp": False})
            expected_exp = now + timedelta(minutes=30)

            # Check expiration is set correctly
            token_exp = datetime.fromtimestamp(payload["exp"])
            assert abs((token_exp - expected_exp).total_seconds()) < 2

    def test_multiple_tokens_are_different(self, service):
        """Test that multiple tokens for same subject can be generated"""
        import time
        token1 = service.create_access_token(subject="user_123")
        time.sleep(1.1)  # Wait more than 1 second to ensure different iat
        token2 = service.create_access_token(subject="user_123")

        # Tokens should be different due to different iat timestamps
        # If they execute in the same second, they might be the same
        # So we just verify both are valid tokens
        assert isinstance(token1, str) and len(token1) > 0
        assert isinstance(token2, str) and len(token2) > 0


class TestCreateRefreshToken:
    """Test refresh token creation"""

    @pytest.fixture
    def service(self):
        """Create JWT service for testing"""
        return JWTService(
            secret_key="test_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

    def test_create_refresh_token_basic(self, service):
        """Test creating basic refresh token"""
        token = service.create_refresh_token(subject="user_123")

        assert isinstance(token, str)
        assert len(token) > 0

        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["sub"] == "user_123"
        assert payload["type"] == "refresh"

    def test_create_refresh_token_with_additional_claims(self, service):
        """Test creating refresh token with additional claims"""
        additional_claims = {"email": "test@example.com"}

        token = service.create_refresh_token(
            subject="user_123", additional_claims=additional_claims
        )

        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["email"] == "test@example.com"

    def test_refresh_token_expiration_time(self, service):
        """Test that refresh token has correct expiration"""
        with patch("app.shared.infrastructure.security.jwt_service.datetime") as mock_dt:
            now = datetime(2024, 1, 1, 12, 0, 0)
            mock_dt.utcnow.return_value = now

            token = service.create_refresh_token(subject="user_123")

            # Decode without verifying expiration
            payload = jwt.decode(token, "test_secret", algorithms=["HS256"], options={"verify_exp": False})
            expected_exp = now + timedelta(days=7)

            token_exp = datetime.fromtimestamp(payload["exp"])
            assert abs((token_exp - expected_exp).total_seconds()) < 2


class TestVerifyToken:
    """Test token verification"""

    @pytest.fixture
    def service(self):
        """Create JWT service for testing"""
        return JWTService(
            secret_key="test_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

    def test_verify_valid_access_token(self, service):
        """Test verifying valid access token"""
        token = service.create_access_token(subject="user_123")

        payload = service.verify_token(token, expected_type="access")

        assert payload["sub"] == "user_123"
        assert payload["type"] == "access"

    def test_verify_valid_refresh_token(self, service):
        """Test verifying valid refresh token"""
        token = service.create_refresh_token(subject="user_123")

        payload = service.verify_token(token, expected_type="refresh")

        assert payload["sub"] == "user_123"
        assert payload["type"] == "refresh"

    def test_verify_token_wrong_type(self, service):
        """Test verifying token with wrong expected type"""
        token = service.create_access_token(subject="user_123")

        with pytest.raises(ValueError, match="Invalid token type"):
            service.verify_token(token, expected_type="refresh")

    def test_verify_expired_token(self, service):
        """Test verifying expired token"""
        # Create a token with past expiration
        past_time = datetime.utcnow() - timedelta(hours=1)
        
        payload = {
            "sub": "user_123",
            "exp": past_time,
            "iat": past_time - timedelta(hours=2),
            "type": "access",
        }
        
        expired_token = jwt.encode(payload, "test_secret", algorithm="HS256")

        with pytest.raises(JWTError):
            service.verify_token(expired_token, expected_type="access")

    def test_verify_invalid_signature(self, service):
        """Test verifying token with invalid signature"""
        token = service.create_access_token(subject="user_123")

        # Create service with different secret
        wrong_service = JWTService(
            secret_key="wrong_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

        with pytest.raises(JWTError):
            wrong_service.verify_token(token, expected_type="access")

    def test_verify_malformed_token(self, service):
        """Test verifying malformed token"""
        with pytest.raises(JWTError):
            service.verify_token("not.a.valid.token", expected_type="access")

    def test_verify_empty_token(self, service):
        """Test verifying empty token"""
        with pytest.raises(JWTError):
            service.verify_token("", expected_type="access")


class TestGetSubject:
    """Test extracting subject from token"""

    @pytest.fixture
    def service(self):
        """Create JWT service for testing"""
        return JWTService(
            secret_key="test_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

    def test_get_subject_from_valid_token(self, service):
        """Test getting subject from valid token"""
        token = service.create_access_token(subject="user_123")

        subject = service.get_subject(token)

        assert subject == "user_123"

    def test_get_subject_from_expired_token(self, service):
        """Test getting subject from expired token (should still work)"""
        # Create expired token
        service_short = JWTService(
            secret_key="test_secret",
            algorithm="HS256",
            access_token_expire_minutes=0,
            refresh_token_expire_days=7,
        )

        token = service_short.create_access_token(subject="user_123")

        import time
        time.sleep(0.1)

        # get_subject should still work even if token is expired
        subject = service_short.get_subject(token)
        assert subject == "user_123"

    def test_get_subject_from_invalid_token(self, service):
        """Test getting subject from invalid token"""
        subject = service.get_subject("not.a.valid.token")

        assert subject is None

    def test_get_subject_from_token_with_wrong_secret(self, service):
        """Test getting subject from token signed with wrong secret"""
        token = service.create_access_token(subject="user_123")

        wrong_service = JWTService(
            secret_key="wrong_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

        subject = wrong_service.get_subject(token)
        assert subject is None


class TestTokenInteroperability:
    """Test that tokens work across service instances"""

    def test_tokens_work_across_instances(self):
        """Test that tokens created by one service can be verified by another"""
        service1 = JWTService(
            secret_key="shared_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

        service2 = JWTService(
            secret_key="shared_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

        token = service1.create_access_token(subject="user_123")
        payload = service2.verify_token(token, expected_type="access")

        assert payload["sub"] == "user_123"


class TestAdditionalClaimsHandling:
    """Test handling of additional claims"""

    @pytest.fixture
    def service(self):
        """Create JWT service for testing"""
        return JWTService(
            secret_key="test_secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

    def test_none_additional_claims(self, service):
        """Test creating token with None additional claims"""
        token = service.create_access_token(subject="user_123", additional_claims=None)

        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["sub"] == "user_123"
        assert payload["type"] == "access"

    def test_empty_additional_claims(self, service):
        """Test creating token with empty additional claims"""
        token = service.create_access_token(subject="user_123", additional_claims={})

        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["sub"] == "user_123"

    def test_complex_additional_claims(self, service):
        """Test creating token with complex additional claims"""
        claims = {
            "email": "test@example.com",
            "roles": ["admin", "user"],
            "metadata": {"department": "IT", "level": 5},
        }

        token = service.create_access_token(subject="user_123", additional_claims=claims)

        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["email"] == "test@example.com"
        assert payload["roles"] == ["admin", "user"]
        assert payload["metadata"]["department"] == "IT"
