"""Dependency Injection Container.

IoC container for managing application dependencies using dependency-injector.
Follows modular DDD architecture with separate containers for each module.
"""
from dependency_injector import containers, providers

from .config import settings
from .shared.infrastructure.database.connection import db_connection
from .shared.infrastructure.external.gcs_storage_service import gcs_storage_service
from .shared.infrastructure.security.jwt_service import jwt_service
from .shared.infrastructure.security.password_hasher import password_hasher


class SharedContainer(containers.DeclarativeContainer):
    """Shared Kernel container.

    Provides shared services and infrastructure components.
    """

    # Configuration
    config = providers.Singleton(lambda: settings)

    # Database
    db_connection_provider = providers.Singleton(lambda: db_connection)

    # Security Services
    jwt_service_provider = providers.Singleton(lambda: jwt_service)
    password_hasher_provider = providers.Singleton(lambda: password_hasher)

    # External Services
    gcs_storage_provider = providers.Singleton(lambda: gcs_storage_service)


class IdentityModuleContainer(containers.DeclarativeContainer):
    """Identity module container.

    Provides identity and authentication related dependencies.
    """

    # Shared dependencies
    shared = providers.DependenciesContainer()

    # Repositories will be added when implementing US1
    # user_repository = providers.Factory(...)
    # profile_repository = providers.Factory(...)
    # refresh_token_repository = providers.Factory(...)

    # Use Cases will be added when implementing US1
    # google_login_use_case = providers.Factory(...)
    # refresh_token_use_case = providers.Factory(...)


class SocialModuleContainer(containers.DeclarativeContainer):
    """Social module container.

    Provides social features related dependencies.
    """

    # Shared dependencies
    shared = providers.DependenciesContainer()

    # Repositories will be added when implementing US2+
    # card_repository = providers.Factory(...)
    # friendship_repository = providers.Factory(...)

    # Use Cases will be added when implementing US2+
    # upload_card_use_case = providers.Factory(...)


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container.

    Aggregates all module containers and provides application-wide dependencies.
    """

    # Wire configuration - modules that need dependency injection
    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.modules.identity",
            "app.modules.social",
            "app.shared"
        ]
    )

    # Shared Kernel
    shared = providers.Container(SharedContainer)

    # Module Containers
    identity = providers.Container(
        IdentityModuleContainer,
        shared=shared
    )

    social = providers.Container(
        SocialModuleContainer,
        shared=shared
    )


# Global container instance
container = ApplicationContainer()
