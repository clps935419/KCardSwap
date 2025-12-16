"""Database connection management.

This module provides database connection using SQLAlchemy Engine.
"""
from typing import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


class DatabaseConnection:
    """Manages database connections using SQLAlchemy."""

    def __init__(self) -> None:
        """Initialize database connection."""
        self._engine: Engine | None = None
        self._session_factory: sessionmaker | None = None

    @property
    def engine(self) -> Engine:
        """Get or create SQLAlchemy engine.

        Returns:
            SQLAlchemy Engine instance
        """
        if self._engine is None:
            self._engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=settings.DEBUG
            )
        return self._engine

    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory.

        Returns:
            SQLAlchemy sessionmaker
        """
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
        return self._session_factory

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

    def close(self) -> None:
        """Close database engine and connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database connection instance
db_connection = DatabaseConnection()
