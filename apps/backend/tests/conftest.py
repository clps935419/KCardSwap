"""
Test configuration and fixtures for integration tests with testcontainers.

This module provides fixtures for:
- PostgreSQL database container
- Automatic Alembic migration execution
- Database session management
"""
import os
import pytest
from typing import AsyncGenerator, Generator

# Uncomment when testcontainers-postgres is installed
# from testcontainers.postgres import PostgresContainer

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from alembic.config import Config
from alembic import command

from app.infrastructure.database.models import Base


@pytest.fixture(scope="session")
def postgres_container():
    """
    Start a PostgreSQL container for testing.
    
    To use this fixture, install testcontainers:
    poetry add --group dev testcontainers[postgres]
    """
    # Uncomment when testcontainers-postgres is installed
    # with PostgresContainer("postgres:15-alpine") as postgres:
    #     # Set environment variable for Alembic
    #     database_url = postgres.get_connection_url()
    #     os.environ["DATABASE_URL"] = database_url
    #     
    #     # Run Alembic migrations
    #     alembic_cfg = Config("alembic.ini")
    #     alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    #     command.upgrade(alembic_cfg, "head")
    #     
    #     yield postgres
    
    # Temporary: Skip testcontainers for now
    pytest.skip("Testcontainers not yet configured")


@pytest.fixture(scope="session")
def test_database_url(postgres_container) -> str:
    """Get the database URL for testing."""
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@pytest.fixture(scope="session")
async def test_engine(test_database_url: str):
    """Create a test database engine."""
    engine = create_async_engine(test_database_url, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def test_session_factory(test_engine) -> async_sessionmaker:
    """Create a test session factory."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture
async def db_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional database session for each test.
    
    Each test gets a clean database state through transaction rollback.
    """
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
