"""Application configuration.

This module provides centralized configuration management using environment variables.
"""

import os


class Settings:
    """Application configuration class.

    Centralizes all configuration values from environment variables.
    """

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/kcardswap"
    )
    TEST_DATABASE_URL: str = os.getenv(
        "TEST_DATABASE_URL", "postgresql+asyncpg://kcardswap:kcardswap@localhost:5432/kcardswap_test"
    )

    # JWT
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Cookie-JWT Settings (for Web POC)
    # Cookie names for access and refresh tokens
    ACCESS_COOKIE_NAME: str = os.getenv("ACCESS_COOKIE_NAME", "access_token")
    REFRESH_COOKIE_NAME: str = os.getenv("REFRESH_COOKIE_NAME", "refresh_token")
    # Cookie security settings
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax")  # lax, strict, none
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # true for HTTPS
    COOKIE_HTTPONLY: bool = True  # Always httpOnly for security
    COOKIE_DOMAIN: str | None = os.getenv("COOKIE_DOMAIN")  # None for same-origin
    COOKIE_PATH: str = "/"  # Root path for all cookies

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")

    # GCS (Google Cloud Storage)
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "kcardswap")
    GCS_CREDENTIALS_PATH: str | None = os.getenv("GCS_CREDENTIALS_PATH")
    # Use mock GCS for development/testing (default: true for dev, false for production)
    USE_MOCK_GCS: bool = os.getenv("USE_MOCK_GCS", "true").lower() == "true"
    # Enable GCS smoke tests (only for staging/nightly, default: false)
    RUN_GCS_SMOKE: bool = os.getenv("RUN_GCS_SMOKE", "false").lower() == "true"

    # FCM (Firebase Cloud Messaging)
    FCM_CREDENTIALS_PATH: str | None = os.getenv("FCM_CREDENTIALS_PATH")

    # File Upload Limits
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    DAILY_UPLOAD_LIMIT_FREE: int = int(os.getenv("DAILY_UPLOAD_LIMIT_FREE", "2"))
    TOTAL_STORAGE_GB_FREE: int = int(os.getenv("TOTAL_STORAGE_GB_FREE", "1"))

    # Nearby Search Limits
    DAILY_SEARCH_LIMIT_FREE: int = int(os.getenv("DAILY_SEARCH_LIMIT_FREE", "5"))
    SEARCH_RADIUS_KM: float = float(os.getenv("SEARCH_RADIUS_KM", "10.0"))

    # Trade Configuration
    TRADE_CONFIRMATION_TIMEOUT_HOURS: int = int(
        os.getenv("TRADE_CONFIRMATION_TIMEOUT_HOURS", "48")
    )

    # Google Play Billing (Subscription)
    GOOGLE_PLAY_PACKAGE_NAME: str = os.getenv("GOOGLE_PLAY_PACKAGE_NAME", "")
    GOOGLE_PLAY_SERVICE_ACCOUNT_KEY_PATH: str | None = os.getenv(
        "GOOGLE_PLAY_SERVICE_ACCOUNT_KEY_PATH"
    )

    # API
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL", "INFO"
    )  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Security
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


# Global configuration instance
settings = Settings()

# For backward compatibility
config = settings


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
