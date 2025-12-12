"""
Dependency Providers for FastAPI Routes
Uses IoC container to inject dependencies following DIP
"""
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import Provide, inject

from ..container import Container
from ...domain.repositories.user_repository_interface import IUserRepository
from ...domain.repositories.profile_repository_interface import IProfileRepository
from ...infrastructure.external.google_oauth_service import GoogleOAuthService
from ...infrastructure.security.jwt_service import JWTService
from ...infrastructure.database.connection import get_db_session


# Database session provider
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session from container"""
    async for session in get_db_session():
        yield session


# Repository providers using IoC container
@inject
def get_user_repository(
    session: AsyncSession = Depends(get_session),
    container: Container = Depends(lambda: Container())
) -> IUserRepository:
    """
    Get user repository instance
    Depends on database session and returns interface, not concrete implementation
    """
    from ...infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
    return SQLAlchemyUserRepository(session)


@inject
def get_profile_repository(
    session: AsyncSession = Depends(get_session),
    container: Container = Depends(lambda: Container())
) -> IProfileRepository:
    """
    Get profile repository instance
    Depends on database session and returns interface, not concrete implementation
    """
    from ...infrastructure.repositories.sqlalchemy_profile_repository import SQLAlchemyProfileRepository
    return SQLAlchemyProfileRepository(session)


# Service providers using IoC container
@inject
def get_google_oauth_service(
    container: Container = Depends(lambda: Container())
) -> GoogleOAuthService:
    """Get Google OAuth service instance"""
    return container.google_oauth_service()


@inject
def get_jwt_service(
    container: Container = Depends(lambda: Container())
) -> JWTService:
    """Get JWT service instance"""
    return container.jwt_service()
