"""Shared Module for dependency injection.

Provides shared services and infrastructure components using python-injector.
"""

from injector import Module, provider, singleton

from app.config import Settings, settings
from app.shared.infrastructure.database.connection import (
    DatabaseConnection,
    db_connection,
)
from app.shared.infrastructure.external import storage_service_factory
from app.shared.infrastructure.external.gcs_storage_service import GCSStorageService
from app.shared.infrastructure.security.jwt_service import JWTService, jwt_service
from app.shared.infrastructure.security.password_hasher import (
    PasswordHasher,
    password_hasher,
)


class SharedModule(Module):
    """Shared Kernel module for python-injector.

    Provides shared services and infrastructure components.
    """

    @provider
    @singleton
    def provide_settings(self) -> Settings:
        """Provide application settings."""
        return settings

    @provider
    @singleton
    def provide_db_connection(self) -> DatabaseConnection:
        """Provide database connection."""
        return db_connection

    @provider
    @singleton
    def provide_jwt_service(self) -> JWTService:
        """Provide JWT service."""
        return jwt_service

    @provider
    @singleton
    def provide_password_hasher(self) -> PasswordHasher:
        """Provide password hasher."""
        return password_hasher

    @provider
    @singleton
    def provide_gcs_storage(self) -> GCSStorageService:
        """Provide GCS storage service."""
        return storage_service_factory.storage_service
