"""
Database infrastructure __init__

This module provides database connectivity and ORM models for the application.
All schema changes must be managed through Alembic migrations (see docs/database-migrations.md).
"""
from .connection import engine, get_db, get_db_session, init_db
from .models import Base, ProfileModel, RefreshTokenModel, UserModel

__all__ = [
    "get_db_session",
    "get_db",
    "init_db",  # Deprecated: kept for backward compatibility
    "engine",
    "Base",
    "UserModel",
    "ProfileModel",
    "RefreshTokenModel",
]
