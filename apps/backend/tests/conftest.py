"""
Test configuration and fixtures for integration tests.

This module provides fixtures for:
- PostgreSQL test database (separate from main database)
- Automatic Alembic migration execution
- Database session management with transaction rollback
- GCS mock service for testing
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.shared.infrastructure.external import storage_service_factory
from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)
from app.shared.infrastructure.security.jwt_service import JWTService

# Ensure GCS is mocked before importing the app (affects DI initialization)
settings.USE_MOCK_GCS = True
settings.GCS_BUCKET_NAME = "kcardswap-test"
settings.GCS_CREDENTIALS_PATH = None
storage_service_factory.storage_service = MockGCSStorageService(
    bucket_name=settings.GCS_BUCKET_NAME,
    credentials_path=settings.GCS_CREDENTIALS_PATH,
)

from app.main import app  # noqa: E402
from app.shared.infrastructure.database.connection import get_db_session  # noqa: E402


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


@pytest.fixture(scope="session", autouse=True)
def force_mock_gcs() -> None:
    """Force Mock GCS for all tests to avoid real GCS usage."""
    original_use_mock = settings.USE_MOCK_GCS
    original_bucket = settings.GCS_BUCKET_NAME
    original_credentials = settings.GCS_CREDENTIALS_PATH
    original_storage_service = storage_service_factory.storage_service

    settings.USE_MOCK_GCS = True
    settings.GCS_BUCKET_NAME = "kcardswap-test"
    settings.GCS_CREDENTIALS_PATH = None
    storage_service_factory.storage_service = MockGCSStorageService(
        bucket_name=settings.GCS_BUCKET_NAME,
        credentials_path=settings.GCS_CREDENTIALS_PATH,
    )

    yield

    settings.USE_MOCK_GCS = original_use_mock
    settings.GCS_BUCKET_NAME = original_bucket
    settings.GCS_CREDENTIALS_PATH = original_credentials
    storage_service_factory.storage_service = original_storage_service


@pytest_asyncio.fixture
async def test_engine(test_database_url: str):
    """Create a test database engine for each test.

    Note: Using function scope to avoid event loop issues with pytest-asyncio.
    While this creates a new engine for each test, the performance impact is
    acceptable for small to medium test suites. For larger suites, consider
    using session scope with proper event loop management.

    Args:
        test_database_url: Database URL for testing

    Yields:
        AsyncEngine: SQLAlchemy async engine for testing
    """
    engine = create_async_engine(test_database_url, echo=False, pool_pre_ping=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session_factory(test_engine) -> async_sessionmaker:
    """Create a test session factory for each test.

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
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for each test (committable)."""
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db(test_engine):
    """Truncate all public tables after each test to keep DB clean."""
    yield
    async with test_engine.begin() as connection:
        result = await connection.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename != 'alembic_version'
                """
            )
        )
        tables = [row[0] for row in result.fetchall()]
        if tables:
            table_list = ", ".join(f'"{name}"' for name in tables)
            await connection.execute(text(f"TRUNCATE TABLE {table_list} CASCADE"))


@pytest_asyncio.fixture(autouse=True)
async def ensure_gallery_cards_table(test_engine) -> None:
    """Ensure gallery_cards table exists for integration tests."""
    async with test_engine.begin() as connection:
        await connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS gallery_cards (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(200) NOT NULL,
                    idol_name VARCHAR(100) NOT NULL,
                    era VARCHAR(100) NULL,
                    description TEXT NULL,
                    media_asset_id UUID NULL,
                    display_order INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        await connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_gallery_cards_user_id
                ON gallery_cards (user_id)
                """
            )
        )


@pytest_asyncio.fixture
async def create_user(db_session: AsyncSession):
    """Factory fixture to create a test user and return user ID."""

    async def _create_user(prefix: str = "test", role: str = "user"):
        unique_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
                """
            ),
            {
                "id": user_id,
                "google_id": f"{prefix}_{unique_id}",
                "email": f"{prefix}_{unique_id}@test.com",
                "role": role,
            },
        )
        user_id = result.scalar()
        await db_session.commit()
        return user_id

    return _create_user


@pytest.fixture
def app_db_session_override(test_database_url):
    """Provide override for get_db_session that is safe for TestClient threads."""

    async def _override_get_db_session():
        engine = create_async_engine(test_database_url, echo=False, pool_pre_ping=True)
        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        await engine.dispose()

    return _override_get_db_session


@pytest.fixture(autouse=True)
def override_app_db_session(app_db_session_override):
    """Ensure FastAPI routes use a safe DB session override by default."""
    previous_override = app.dependency_overrides.get(get_db_session)
    app.dependency_overrides[get_db_session] = app_db_session_override

    yield

    if previous_override is not None:
        app.dependency_overrides[get_db_session] = previous_override
    else:
        app.dependency_overrides.pop(get_db_session, None)


@pytest_asyncio.fixture
async def async_client():
    """Provide an AsyncClient for async integration tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def client(async_client):
    """Alias for async_client to match existing tests."""
    return async_client


@pytest_asyncio.fixture
async def user1_id(create_user):
    """Create a test user (user1) and return user ID."""
    return await create_user(prefix="user1")


@pytest_asyncio.fixture
async def user2_id(create_user):
    """Create a test user (user2) and return user ID."""
    return await create_user(prefix="user2")


@pytest.fixture
def auth_headers_user1(user1_id):
    """Provide auth headers for user1."""
    token = JWTService().create_access_token(subject=str(user1_id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2(user2_id):
    """Provide auth headers for user2."""
    token = JWTService().create_access_token(subject=str(user2_id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_post_id(db_session: AsyncSession, user1_id):
    """Create a sample post and return post ID for like tests."""
    post_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=14)
    await db_session.execute(
        text(
            """
            INSERT INTO posts (
                id, owner_id, scope, category, title, content,
                status, expires_at, created_at, updated_at
            )
            VALUES (
                :id, :owner_id, :scope, :category, :title, :content,
                :status, :expires_at, NOW(), NOW()
            )
            """
        ),
        {
            "id": post_id,
            "owner_id": str(user1_id),
            "scope": "global",
            "category": "trade",
            "title": "Sample Post",
            "content": "Sample Content",
            "status": "open",
            "expires_at": expires_at,
        },
    )
    await db_session.commit()
    return post_id
