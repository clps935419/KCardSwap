"""Base Entity class for Domain entities.

This module provides the base class for all domain entities following DDD principles.
"""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


class BaseEntity:
    """Base class for all domain entities.

    Provides identity, equality, and lifecycle management for domain entities.
    Entities are identified by their ID, not by their attributes.
    """

    def __init__(
        self,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ) -> None:
        """Initialize base entity.

        Args:
            id: Unique identifier (generated if not provided)
            created_at: Creation timestamp (set to now if not provided)
            updated_at: Last update timestamp (set to now if not provided)
        """
        self._id = id or uuid4()
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> UUID:
        """Get entity ID."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    def mark_updated(self) -> None:
        """Mark entity as updated (sets updated_at to current time)."""
        self._updated_at = datetime.utcnow()

    def __eq__(self, other: Any) -> bool:
        """Check equality based on entity ID.

        Two entities are equal if they have the same ID and type.
        """
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash based on entity ID."""
        return hash(self._id)

    def __repr__(self) -> str:
        """Developer representation of entity."""
        return f"{self.__class__.__name__}(id={self._id})"
