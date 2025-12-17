"""JWT Service for authentication token management.

This module provides JWT token generation and verification for access and refresh tokens.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.config import settings


class JWTService:
    """Service for JWT token operations.

    Handles generation and verification of access and refresh tokens.
    """

    def __init__(
        self,
        secret_key: str = settings.JWT_SECRET_KEY,
        algorithm: str = settings.JWT_ALGORITHM,
        access_token_expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS,
    ) -> None:
        """Initialize JWT service.

        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (e.g., HS256, RS256)
            access_token_expire_minutes: Access token expiration time in minutes
            refresh_token_expire_days: Refresh token expiration time in days
        """
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self, subject: str, additional_claims: Dict[str, Any] | None = None
    ) -> str:
        """Create an access token.

        Args:
            subject: Subject (usually user_id)
            additional_claims: Additional claims to include in token

        Returns:
            Encoded JWT access token
        """
        expire = datetime.utcnow() + timedelta(
            minutes=self._access_token_expire_minutes
        )

        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }

        if additional_claims:
            to_encode.update(additional_claims)

        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(
        self, subject: str, additional_claims: Dict[str, Any] | None = None
    ) -> str:
        """Create a refresh token.

        Args:
            subject: Subject (usually user_id)
            additional_claims: Additional claims to include in token

        Returns:
            Encoded JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(days=self._refresh_token_expire_days)

        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        if additional_claims:
            to_encode.update(additional_claims)

        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str, expected_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token.

        Args:
            token: JWT token to verify
            expected_type: Expected token type ('access' or 'refresh')

        Returns:
            Decoded token payload

        Raises:
            JWTError: If token is invalid or expired
            ValueError: If token type doesn't match expected type
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

            # Verify token type
            token_type = payload.get("type")
            if token_type != expected_type:
                raise ValueError(
                    f"Invalid token type. Expected '{expected_type}', got '{token_type}'"
                )

            return payload

        except JWTError as e:
            raise JWTError(f"Token verification failed: {str(e)}")

    def get_subject(self, token: str) -> Optional[str]:
        """Extract subject (user_id) from token without full verification.

        Args:
            token: JWT token

        Returns:
            Subject if present, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"verify_exp": False},
            )
            return payload.get("sub")
        except JWTError:
            return None


# Global JWT service instance
jwt_service = JWTService()
