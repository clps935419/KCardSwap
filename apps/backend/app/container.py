"""Dependency Injection Container.

IoC container for managing application dependencies using dependency-injector.
Follows modular DDD architecture with separate containers for each module.
"""

from dependency_injector import containers, providers

from .config import settings
from .modules.identity.container import IdentityModuleContainer
from .modules.posts.container import PostsModuleContainer
from .modules.social.container import SocialModuleContainer
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


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container.

    Aggregates all module containers and provides application-wide dependencies.
    """

    # Shared Kernel
    shared = providers.Container(SharedContainer)

    # Module Containers
    identity = providers.Container(IdentityModuleContainer, shared=shared)

    social = providers.Container(SocialModuleContainer, shared=shared)

    posts = providers.Container(PostsModuleContainer, shared=shared)


# Global container instance
container = ApplicationContainer()
