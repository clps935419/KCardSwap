"""
Unit tests for BaseRepository
Testing base repository functionality and abstract methods
"""

from typing import List, Optional
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from app.shared.domain.base_entity import BaseEntity
from app.shared.infrastructure.database.base_repository import BaseRepository


class ConcreteEntity(BaseEntity):
    """Concrete entity for testing"""

    def __init__(self, id: UUID | None = None, name: str = "test"):
        super().__init__(id=id)
        self.name = name


class ConcreteRepository(BaseRepository[ConcreteEntity]):
    """Concrete repository for testing"""

    def find_by_id(self, id: UUID) -> Optional[ConcreteEntity]:
        """Find entity by ID"""
        # Simple mock implementation
        return ConcreteEntity(id=id)

    def find_all(self, limit: int = 100, offset: int = 0) -> List[ConcreteEntity]:
        """Find all entities"""
        # Simple mock implementation
        return []

    def save(self, entity: ConcreteEntity) -> ConcreteEntity:
        """Save entity"""
        # Simple mock implementation
        return entity

    def delete(self, id: UUID) -> bool:
        """Delete entity"""
        # Simple mock implementation
        return True


class TestRepositoryInitialization:
    """Test repository initialization"""

    def test_repository_requires_session(self):
        """Test that repository requires a session"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        assert repository._session is mock_session

    def test_repository_stores_session(self):
        """Test that repository stores the session"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        assert hasattr(repository, "_session")
        assert repository._session == mock_session


class TestRepositoryTransactionMethods:
    """Test repository transaction methods"""

    def test_commit_calls_session_commit(self):
        """Test that _commit calls session.commit()"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        repository._commit()

        mock_session.commit.assert_called_once()

    def test_rollback_calls_session_rollback(self):
        """Test that _rollback calls session.rollback()"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        repository._rollback()

        mock_session.rollback.assert_called_once()

    def test_flush_calls_session_flush(self):
        """Test that _flush calls session.flush()"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        repository._flush()

        mock_session.flush.assert_called_once()


class TestRepositoryAbstractMethods:
    """Test that abstract methods must be implemented"""

    def test_cannot_instantiate_base_repository_directly(self):
        """Test that BaseRepository cannot be instantiated directly"""
        mock_session = Mock()

        with pytest.raises(TypeError):
            BaseRepository(session=mock_session)

    def test_concrete_repository_can_be_instantiated(self):
        """Test that concrete repository can be instantiated"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        assert isinstance(repository, BaseRepository)
        assert isinstance(repository, ConcreteRepository)

    def test_incomplete_repository_cannot_be_instantiated(self):
        """Test that repository without all methods cannot be instantiated"""

        class IncompleteRepository(BaseRepository[ConcreteEntity]):
            def find_by_id(self, id: UUID) -> Optional[ConcreteEntity]:
                return None

        mock_session = Mock()

        with pytest.raises(TypeError):
            IncompleteRepository(session=mock_session)


class TestRepositoryCRUDMethods:
    """Test repository CRUD methods implementation"""

    def test_find_by_id_returns_entity(self):
        """Test that find_by_id can return entity"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)
        entity_id = uuid4()

        result = repository.find_by_id(entity_id)

        assert result is not None
        assert isinstance(result, ConcreteEntity)
        assert result.id == entity_id

    def test_find_all_returns_list(self):
        """Test that find_all returns a list"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        result = repository.find_all()

        assert isinstance(result, list)

    def test_find_all_accepts_pagination(self):
        """Test that find_all accepts limit and offset"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        result = repository.find_all(limit=10, offset=5)

        assert isinstance(result, list)

    def test_save_returns_entity(self):
        """Test that save returns entity"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)
        entity = ConcreteEntity()

        result = repository.save(entity)

        assert result is entity

    def test_delete_returns_bool(self):
        """Test that delete returns boolean"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)
        entity_id = uuid4()

        result = repository.delete(entity_id)

        assert isinstance(result, bool)


class TestRepositoryGenericType:
    """Test repository generic type handling"""

    def test_repository_is_generic(self):
        """Test that repository is generic over entity type"""

        class Entity1(BaseEntity):
            pass

        class Entity2(BaseEntity):
            pass

        class Repo1(BaseRepository[Entity1]):
            def find_by_id(self, id: UUID) -> Optional[Entity1]:
                return None

            def find_all(self, limit: int = 100, offset: int = 0) -> List[Entity1]:
                return []

            def save(self, entity: Entity1) -> Entity1:
                return entity

            def delete(self, id: UUID) -> bool:
                return True

        class Repo2(BaseRepository[Entity2]):
            def find_by_id(self, id: UUID) -> Optional[Entity2]:
                return None

            def find_all(self, limit: int = 100, offset: int = 0) -> List[Entity2]:
                return []

            def save(self, entity: Entity2) -> Entity2:
                return entity

            def delete(self, id: UUID) -> bool:
                return True

        mock_session = Mock()
        repo1 = Repo1(session=mock_session)
        repo2 = Repo2(session=mock_session)

        assert isinstance(repo1, BaseRepository)
        assert isinstance(repo2, BaseRepository)


class TestRepositorySessionManagement:
    """Test repository session management"""

    def test_repository_uses_same_session_instance(self):
        """Test that repository uses the same session instance"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        repository._commit()
        repository._flush()
        repository._rollback()

        # Verify all methods were called
        assert mock_session.commit.call_count == 1
        assert mock_session.flush.call_count == 1
        assert mock_session.rollback.call_count == 1

    def test_multiple_operations_use_same_session(self):
        """Test that multiple operations use the same session"""
        mock_session = Mock()
        repository = ConcreteRepository(session=mock_session)

        repository._flush()
        repository._commit()

        assert mock_session.flush.call_count == 1
        assert mock_session.commit.call_count == 1
