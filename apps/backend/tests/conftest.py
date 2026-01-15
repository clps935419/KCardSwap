"""
Test configuration and fixtures for integration tests.

This module provides fixtures for:
- PostgreSQL test database (separate from main database)
- Automatic Alembic migration execution
- Database session management with transaction rollback
- GCS mock service for testing
"""

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)


def pytest_configure(config):
    """Register custom markers for pytest."""
    config.addinivalue_line(
        "markers", "gcs_smoke: mark test as GCS smoke test (requires real GCS)"
    )


@pytest.fixture(scope="function")
def mock_gcs_service():
    """Provide a fresh mock GCS service for each test.

    This fixture should be used in unit and integration tests to avoid
    hitting real GCS. The mock service provides the same interface as
    the real GCS service but operates in-memory.

    Returns:
        MockGCSStorageService: A fresh instance of the mock service
    """
    service = MockGCSStorageService(bucket_name="kcardswap-test")
    return service


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Get the test database URL from environment or settings.
    
    Returns:
        str: Test database URL for pytest session
    """
    # Use TEST_DATABASE_URL if available, otherwise use the one from settings
    return os.getenv("TEST_DATABASE_URL", settings.TEST_DATABASE_URL)


@pytest_asyncio.fixture(scope="function")
async def test_engine(test_database_url: str):
    """Create a test database engine for each test function.
    
    Args:
        test_database_url: Database URL for testing
        
    Yields:
        AsyncEngine: SQLAlchemy async engine for testing
    """
    engine = create_async_engine(test_database_url, echo=False, pool_pre_ping=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_factory(test_engine) -> async_sessionmaker:
    """Create a test session factory for each test function.
    
    Args:
        test_engine: Test database engine
        
    Returns:
        async_sessionmaker: Session factory for creating test sessions
    """
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture
async def db_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional database session for each test.

    Each test runs in its own transaction that is automatically rolled back
    after the test completes, ensuring test isolation and clean database state.
    
    This approach:
    - Maintains test isolation (each test starts with clean state)
    - Avoids manual cleanup (automatic rollback)
    - Faster than recreating database (uses transactions)
    - Works with the test database (kcardswap_test)
    
    Args:
        test_session_factory: Session factory from the session-scoped fixture
        
    Yields:
        AsyncSession: Database session for the test
    """
    async with test_session_factory() as session:
        async with session.begin():
            try:
                yield session
            finally:
                # Rollback is automatic when exiting the begin() context
                # This ensures all changes made during the test are discarded
                await session.rollback()
