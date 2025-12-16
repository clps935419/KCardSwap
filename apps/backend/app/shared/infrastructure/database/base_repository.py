"""Base Repository class for data access.

This module provides the base repository interface following DDD principles.
"""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.shared.domain.base_entity import BaseEntity

EntityType = TypeVar('EntityType', bound=BaseEntity)


class BaseRepository(ABC, Generic[EntityType]):
    """Base repository interface for domain entities.

    Provides common CRUD operations that can be implemented by concrete repositories.
    """

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations
        """
        self._session = session

    @abstractmethod
    def find_by_id(self, id: UUID) -> Optional[EntityType]:
        """Find entity by ID.

        Args:
            id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[EntityType]:
        """Find all entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    def save(self, entity: EntityType) -> EntityType:
        """Save (create or update) entity.

        Args:
            entity: Entity to save

        Returns:
            Saved entity
        """
        pass

    @abstractmethod
    def delete(self, id: UUID) -> bool:
        """Delete entity by ID.

        Args:
            id: Entity ID

        Returns:
            True if entity was deleted, False if not found
        """
        pass

    def _commit(self) -> None:
        """Commit current transaction."""
        self._session.commit()

    def _rollback(self) -> None:
        """Rollback current transaction."""
        self._session.rollback()

    def _flush(self) -> None:
        """Flush pending changes to database."""
        self._session.flush()
