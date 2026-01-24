"""
Unit tests for BaseEntity
Testing entity identity, equality, and lifecycle management
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest

from app.shared.domain.base_entity import BaseEntity


class TestEntityCreation:
    """Test entity creation and initialization"""

    def test_create_entity_with_defaults(self):
        """Test creating entity with default values"""
        entity = BaseEntity()

        assert isinstance(entity.id, UUID)
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)

    def test_create_entity_with_id(self):
        """Test creating entity with specified ID"""
        entity_id = uuid4()
        entity = BaseEntity(id=entity_id)

        assert entity.id == entity_id

    def test_create_entity_with_timestamps(self):
        """Test creating entity with specified timestamps"""
        created = datetime(2024, 1, 1, 12, 0, 0)
        updated = datetime(2024, 1, 2, 12, 0, 0)

        entity = BaseEntity(created_at=created, updated_at=updated)

        assert entity.created_at == created
        assert entity.updated_at == updated

    def test_create_entity_with_all_fields(self):
        """Test creating entity with all fields specified"""
        entity_id = uuid4()
        created = datetime(2024, 1, 1, 12, 0, 0)
        updated = datetime(2024, 1, 2, 12, 0, 0)

        entity = BaseEntity(id=entity_id, created_at=created, updated_at=updated)

        assert entity.id == entity_id
        assert entity.created_at == created
        assert entity.updated_at == updated


class TestEntityIdentity:
    """Test entity identity and properties"""

    def test_id_is_readonly(self):
        """Test that entity ID cannot be modified"""
        entity = BaseEntity()

        with pytest.raises(AttributeError):
            entity.id = uuid4()

    def test_created_at_is_readonly(self):
        """Test that created_at cannot be modified"""
        entity = BaseEntity()

        with pytest.raises(AttributeError):
            entity.created_at = datetime.utcnow()

    def test_updated_at_is_readonly(self):
        """Test that updated_at cannot be modified directly"""
        entity = BaseEntity()

        with pytest.raises(AttributeError):
            entity.updated_at = datetime.utcnow()


class TestEntityLifecycle:
    """Test entity lifecycle management"""

    def test_mark_updated_changes_timestamp(self):
        """Test that mark_updated updates the timestamp"""
        entity = BaseEntity()
        original_updated_at = entity.updated_at

        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)

        entity.mark_updated()

        assert entity.updated_at > original_updated_at

    def test_mark_updated_does_not_change_created_at(self):
        """Test that mark_updated does not change created_at"""
        entity = BaseEntity()
        original_created_at = entity.created_at

        entity.mark_updated()

        assert entity.created_at == original_created_at

    def test_mark_updated_does_not_change_id(self):
        """Test that mark_updated does not change ID"""
        entity = BaseEntity()
        original_id = entity.id

        entity.mark_updated()

        assert entity.id == original_id


class TestEntityEquality:
    """Test entity equality and hashing"""

    def test_entities_with_same_id_are_equal(self):
        """Test that entities with same ID are equal"""
        entity_id = uuid4()
        created = datetime(2024, 1, 1, 12, 0, 0)

        entity1 = BaseEntity(id=entity_id, created_at=created)
        entity2 = BaseEntity(id=entity_id, created_at=datetime.utcnow())

        assert entity1 == entity2

    def test_entities_with_different_ids_are_not_equal(self):
        """Test that entities with different IDs are not equal"""
        entity1 = BaseEntity()
        entity2 = BaseEntity()

        assert entity1 != entity2

    def test_entity_not_equal_to_non_entity(self):
        """Test that entity is not equal to non-entity object"""
        entity = BaseEntity()

        assert entity != "not an entity"
        assert entity != 123
        assert entity is not None

    def test_entity_hash(self):
        """Test that entity can be hashed"""
        entity = BaseEntity()

        # Should not raise
        hash(entity)

    def test_entities_with_same_id_have_same_hash(self):
        """Test that entities with same ID have same hash"""
        entity_id = uuid4()

        entity1 = BaseEntity(id=entity_id)
        entity2 = BaseEntity(id=entity_id)

        assert hash(entity1) == hash(entity2)

    def test_entity_can_be_used_in_set(self):
        """Test that entity can be used in a set"""
        entity1 = BaseEntity()
        entity2 = BaseEntity()

        entity_set = {entity1, entity2}

        assert len(entity_set) == 2
        assert entity1 in entity_set
        assert entity2 in entity_set

    def test_entity_can_be_used_as_dict_key(self):
        """Test that entity can be used as a dictionary key"""
        entity1 = BaseEntity()
        entity2 = BaseEntity()

        entity_dict = {entity1: "value1", entity2: "value2"}

        assert entity_dict[entity1] == "value1"
        assert entity_dict[entity2] == "value2"


class TestEntityRepresentation:
    """Test entity string representation"""

    def test_entity_repr(self):
        """Test entity __repr__ method"""
        entity_id = uuid4()
        entity = BaseEntity(id=entity_id)

        repr_str = repr(entity)

        assert "BaseEntity" in repr_str
        assert str(entity_id) in repr_str


class TestSubclassingBehavior:
    """Test that BaseEntity works correctly as a base class"""

    def test_subclass_equality_different_types(self):
        """Test that different subclasses are not equal"""

        class Entity1(BaseEntity):
            pass

        class Entity2(BaseEntity):
            pass

        entity_id = uuid4()
        entity1 = Entity1(id=entity_id)
        entity2 = Entity2(id=entity_id)

        assert entity1 != entity2

    def test_subclass_repr_uses_correct_class_name(self):
        """Test that subclass __repr__ uses the subclass name"""

        class CustomEntity(BaseEntity):
            pass

        entity = CustomEntity()
        repr_str = repr(entity)

        assert "CustomEntity" in repr_str
        assert "BaseEntity" not in repr_str
