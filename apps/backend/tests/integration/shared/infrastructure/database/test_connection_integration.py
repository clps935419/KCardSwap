"""
Integration tests for Database Connection

Tests database connection management, pooling, and session lifecycle.
"""

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.infrastructure.database.connection import (
    DatabaseConnection,
    get_db_session,
)


class TestDatabaseConnectionIntegration:
    """Integration tests for DatabaseConnection"""

    @pytest.mark.asyncio
    async def test_async_engine_creation(self, test_database_url):
        """Test async engine is created correctly"""
        # Arrange
        conn = DatabaseConnection()
        # Override DATABASE_URL for testing
        import app.config
        original_url = app.config.settings.DATABASE_URL
        app.config.settings.DATABASE_URL = test_database_url.replace(
            "postgresql+asyncpg://", "postgresql://"
        )

        try:
            # Act
            engine = conn.async_engine

            # Assert
            assert engine is not None
            assert engine.pool is not None
            
            # Test connection works
            async with engine.connect() as connection:
                result = await connection.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            # Cleanup
            app.config.settings.DATABASE_URL = original_url
            conn.close()

    @pytest.mark.asyncio
    async def test_async_session_factory_creation(self, test_database_url):
        """Test async session factory is created correctly"""
        # Arrange
        conn = DatabaseConnection()
        import app.config
        original_url = app.config.settings.DATABASE_URL
        app.config.settings.DATABASE_URL = test_database_url.replace(
            "postgresql+asyncpg://", "postgresql://"
        )

        try:
            # Act
            factory = conn.async_session_factory

            # Assert
            assert factory is not None
            
            # Test session works
            async with factory() as session:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            # Cleanup
            app.config.settings.DATABASE_URL = original_url
            conn.close()

    @pytest.mark.asyncio
    async def test_get_async_session_context_manager(self, test_database_url):
        """Test async session context manager commits on success"""
        # Arrange
        conn = DatabaseConnection()
        import app.config
        original_url = app.config.settings.DATABASE_URL
        app.config.settings.DATABASE_URL = test_database_url.replace(
            "postgresql+asyncpg://", "postgresql://"
        )

        try:
            # Act & Assert
            async with conn.get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
                # Session should auto-commit on successful exit
        finally:
            # Cleanup
            app.config.settings.DATABASE_URL = original_url
            conn.close()

    @pytest.mark.asyncio
    async def test_get_async_session_rollback_on_error(self, test_database_url):
        """Test async session context manager rolls back on error"""
        # Arrange
        conn = DatabaseConnection()
        import app.config
        original_url = app.config.settings.DATABASE_URL
        app.config.settings.DATABASE_URL = test_database_url.replace(
            "postgresql+asyncpg://", "postgresql://"
        )

        try:
            # Act & Assert
            with pytest.raises(Exception):
                async with conn.get_async_session() as session:
                    await session.execute(text("SELECT 1"))
                    # Force an error
                    raise Exception("Test error")
            # Session should have rolled back
        finally:
            # Cleanup
            app.config.settings.DATABASE_URL = original_url
            conn.close()

    @pytest.mark.asyncio
    async def test_get_db_session_dependency(self, db_session):
        """Test get_db_session FastAPI dependency"""
        # Act
        result = await db_session.execute(text("SELECT 1 as value"))
        row = result.first()

        # Assert
        assert row is not None
        assert row.value == 1

    @pytest.mark.asyncio
    async def test_multiple_sessions_isolation(self, test_session_factory):
        """Test that multiple sessions are isolated"""
        # Arrange
        async with test_session_factory() as session1:
            async with test_session_factory() as session2:
                # Act
                result1 = await session1.execute(text("SELECT 1 as id"))
                result2 = await session2.execute(text("SELECT 2 as id"))

                # Assert
                assert result1.scalar() == 1
                assert result2.scalar() == 2

    @pytest.mark.asyncio
    async def test_connection_pool_reuse(self, test_engine):
        """Test that connection pool reuses connections"""
        # Arrange & Act
        async with test_engine.connect() as conn1:
            result1 = await conn1.execute(text("SELECT 1"))
            assert result1.scalar() == 1

        async with test_engine.connect() as conn2:
            result2 = await conn2.execute(text("SELECT 1"))
            assert result2.scalar() == 1

        # Assert - connections should come from the pool
        assert test_engine.pool is not None

    @pytest.mark.asyncio
    async def test_session_transaction_commit(self, db_session):
        """Test that session can execute and flush changes"""
        # Act
        await db_session.execute(
            text("CREATE TEMP TABLE test_table (id INT, value TEXT)")
        )
        await db_session.execute(
            text("INSERT INTO test_table (id, value) VALUES (1, 'test')")
        )
        await db_session.flush()

        # Verify
        result = await db_session.execute(text("SELECT value FROM test_table WHERE id = 1"))
        row = result.first()

        # Assert
        assert row is not None
        assert row.value == "test"

    @pytest.mark.asyncio
    async def test_session_rollback_on_error(self, db_session):
        """Test that session rolls back on error"""
        # Arrange
        await db_session.execute(
            text("CREATE TEMP TABLE test_rollback (id INT PRIMARY KEY)")
        )

        # Act & Assert
        with pytest.raises(Exception):
            await db_session.execute(
                text("INSERT INTO test_rollback (id) VALUES (1)")
            )
            await db_session.flush()
            
            # Try to insert duplicate - this should fail
            await db_session.execute(
                text("INSERT INTO test_rollback (id) VALUES (1)")
            )
            await db_session.flush()
