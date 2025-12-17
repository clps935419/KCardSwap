"""Application configuration.

This module provides centralized configuration management using environment variables.
"""

import os


class Config:
    """Application configuration class.

    Centralizes all configuration values from environment variables.
    """

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/kcardswap"
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

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")

    # GCS (Google Cloud Storage)
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "kcardswap")
    GCS_CREDENTIALS_PATH: str | None = os.getenv("GCS_CREDENTIALS_PATH")

    # File Upload Limits
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    DAILY_UPLOAD_LIMIT_FREE: int = int(os.getenv("DAILY_UPLOAD_LIMIT_FREE", "2"))
    TOTAL_STORAGE_GB_FREE: int = int(os.getenv("TOTAL_STORAGE_GB_FREE", "1"))

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
settings = Config()

# For backward compatibility
config = settings
