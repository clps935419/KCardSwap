"""Database connection management.

This module provides database connection using SQLAlchemy Engine (both sync and async).
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# Declarative base for ORM models
Base = declarative_base()


class DatabaseConnection:
    """Manages database connections using SQLAlchemy."""

    def __init__(self) -> None:
        """Initialize database connection."""
        self._engine: Engine | None = None
        self._async_engine: AsyncEngine | None = None
        self._session_factory: sessionmaker | None = None
        self._async_session_factory: sessionmaker | None = None

    @property
    def engine(self) -> Engine:
        """Get or create SQLAlchemy engine (sync).

        Returns:
            SQLAlchemy Engine instance
        """
        if self._engine is None:
            self._engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=settings.DEBUG,
            )
        return self._engine

    @property
    def async_engine(self) -> AsyncEngine:
        """Get or create SQLAlchemy async engine.

        Returns:
            SQLAlchemy AsyncEngine instance
        """
        if self._async_engine is None:
            # Convert postgresql:// to postgresql+asyncpg://
            async_url = settings.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
            self._async_engine = create_async_engine(
                async_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=settings.DEBUG,
            )
        return self._async_engine

    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory (sync).

        Returns:
            SQLAlchemy sessionmaker
        """
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine, autocommit=False, autoflush=False
            )
        return self._session_factory

    @property
    def async_session_factory(self) -> sessionmaker:
        """Get or create async session factory.

        Returns:
            SQLAlchemy async sessionmaker
        """
        if self._async_session_factory is None:
            self._async_session_factory = sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        return self._async_session_factory

    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session (context manager).

        Yields:
            SQLAlchemy Session instance

        Example:
            ```python
            with db_connection.get_session() as session:
                # Use session here
                session.query(User).all()
            ```
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session (context manager).

        Yields:
            SQLAlchemy AsyncSession instance

        Example:
            ```python
            async with db_connection.get_async_session() as session:
                # Use session here
                result = await session.execute(select(User))
            ```
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def close(self) -> None:
        """Close database engine and connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
        if self._async_engine:
            # AsyncEngine cleanup handled by async context
            self._async_engine = None
            self._async_session_factory = None


# Global database connection instance
db_connection = DatabaseConnection()


# FastAPI dependency for async database sessions
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting async database session.

    Yields:
        AsyncSession instance

    Example:
        ```python
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_db_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with db_connection.async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
