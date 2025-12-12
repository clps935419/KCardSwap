"""
Dependency Injection Container
IoC container for managing application dependencies
"""
from dependency_injector import containers, providers

from .infrastructure.database.connection import get_db_session
from .infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from .infrastructure.repositories.sqlalchemy_profile_repository import SQLAlchemyProfileRepository
from .infrastructure.external.google_oauth_service import GoogleOAuthService
from .infrastructure.security.jwt_service import JWTService
from .config import Settings


class Container(containers.DeclarativeContainer):
    """
    Application IoC Container
    
    Centralized dependency injection container following DDD principles.
    All dependencies are registered here and injected where needed.
    """
    
    # Configuration
    config = providers.Singleton(Settings)
    
    # Infrastructure Services (Singleton - shared across requests)
    google_oauth_service = providers.Singleton(GoogleOAuthService)
    jwt_service = providers.Singleton(JWTService)
    
    # Database Session Factory (creates new session per request)
    db_session = providers.Resource(get_db_session)
    
    # Repositories (Factory - creates new instance per injection)
    # These depend on db_session which will be provided at call time
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=db_session
    )
    
    profile_repository = providers.Factory(
        SQLAlchemyProfileRepository,
        session=db_session
    )
