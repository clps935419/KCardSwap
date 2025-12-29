"""
Unit tests for User Entity
Testing core business logic and validation rules
"""
from datetime import datetime
from uuid import UUID, uuid4

import pytest

from app.modules.identity.domain.entities.user import User


class TestUserCreation:
    """Test user entity creation and validation"""

    def test_create_user_with_google_id(self):
        """Test creating a user with Google OAuth"""
        user = User(
            email="test@example.com",
            google_id="google_123",
        )

        assert user.email == "test@example.com"
        assert user.google_id == "google_123"
        assert user.password_hash is None
        assert user.role == "user"
        assert isinstance(user.id, UUID)
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_create_user_with_password(self):
        """Test creating a user with password authentication"""
        user = User(
            email="admin@example.com",
            password_hash="hashed_password_123",
            role="admin",
        )

        assert user.email == "admin@example.com"
        assert user.password_hash == "hashed_password_123"
        assert user.google_id is None
        assert user.role == "admin"

    def test_create_user_with_custom_id(self):
        """Test creating a user with a specific ID"""
        custom_id = uuid4()
        user = User(
            email="test@example.com",
            google_id="google_123",
            id=custom_id,
        )

        assert user.id == custom_id

    def test_create_user_with_timestamps(self):
        """Test creating a user with specific timestamps"""
        now = datetime.utcnow()
        user = User(
            email="test@example.com",
            google_id="google_123",
            created_at=now,
            updated_at=now,
        )

        assert user.created_at == now
        assert user.updated_at == now

    def test_email_normalization(self):
        """Test that email is normalized to lowercase"""
        user = User(
            email="Test@EXAMPLE.COM",
            google_id="google_123",
        )

        assert user.email == "test@example.com"


class TestUserValidation:
    """Test user entity validation rules"""

    def test_invalid_email_format(self):
        """Test that invalid email format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                email="invalid-email",
                google_id="google_123",
            )

    def test_empty_email(self):
        """Test that empty email raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                email="",
                google_id="google_123",
            )

    def test_missing_authentication_method(self):
        """Test that user must have either google_id or password_hash"""
        with pytest.raises(
            ValueError, match="Either google_id or password_hash must be provided"
        ):
            User(email="test@example.com")

    def test_invalid_role(self):
        """Test that invalid role raises ValueError"""
        with pytest.raises(
            ValueError, match="Invalid role. Must be 'user', 'admin', or 'super_admin'"
        ):
            User(
                email="test@example.com",
                google_id="google_123",
                role="invalid_role",
            )

    def test_valid_roles(self):
        """Test that all valid roles are accepted"""
        for role in ["user", "admin", "super_admin"]:
            user = User(
                email="test@example.com",
                google_id="google_123",
                role=role,
            )
            assert user.role == role


class TestUserBusinessLogic:
    """Test user entity business logic methods"""

    def test_is_admin_for_admin_role(self):
        """Test is_admin returns True for admin role"""
        user = User(
            email="admin@example.com",
            password_hash="hashed",
            role="admin",
        )

        assert user.is_admin() is True

    def test_is_admin_for_super_admin_role(self):
        """Test is_admin returns True for super_admin role"""
        user = User(
            email="superadmin@example.com",
            password_hash="hashed",
            role="super_admin",
        )

        assert user.is_admin() is True

    def test_is_admin_for_regular_user(self):
        """Test is_admin returns False for regular user"""
        user = User(
            email="user@example.com",
            google_id="google_123",
            role="user",
        )

        assert user.is_admin() is False

    def test_update_email(self):
        """Test updating user email"""
        user = User(
            email="old@example.com",
            google_id="google_123",
        )

        old_updated_at = user.updated_at
        user.update_email("new@example.com")

        assert user.email == "new@example.com"
        assert user.updated_at > old_updated_at

    def test_update_email_normalizes(self):
        """Test that update_email normalizes the new email"""
        user = User(
            email="old@example.com",
            google_id="google_123",
        )

        user.update_email("NEW@EXAMPLE.COM")
        assert user.email == "new@example.com"

    def test_update_email_validates(self):
        """Test that update_email validates the new email"""
        user = User(
            email="old@example.com",
            google_id="google_123",
        )

        with pytest.raises(ValueError, match="Invalid email format"):
            user.update_email("invalid-email")


class TestUserEquality:
    """Test user entity equality and hashing"""

    def test_users_with_same_id_are_equal(self):
        """Test that users with same ID are equal"""
        user_id = uuid4()
        user1 = User(
            email="test1@example.com",
            google_id="google_123",
            id=user_id,
        )
        user2 = User(
            email="test2@example.com",
            google_id="google_456",
            id=user_id,
        )

        assert user1 == user2

    def test_users_with_different_ids_are_not_equal(self):
        """Test that users with different IDs are not equal"""
        user1 = User(
            email="test1@example.com",
            google_id="google_123",
        )
        user2 = User(
            email="test1@example.com",
            google_id="google_123",
        )

        assert user1 != user2

    def test_user_not_equal_to_non_user(self):
        """Test that user is not equal to non-User object"""
        user = User(
            email="test@example.com",
            google_id="google_123",
        )

        assert user != "not a user"
        assert user != 123
        assert user != None

    def test_user_hash(self):
        """Test that user can be hashed (for use in sets/dicts)"""
        user = User(
            email="test@example.com",
            google_id="google_123",
        )

        # Should not raise
        hash(user)

        # Should be usable in sets
        user_set = {user}
        assert user in user_set

    def test_user_repr(self):
        """Test user string representation"""
        user = User(
            email="test@example.com",
            google_id="google_123",
        )

        repr_str = repr(user)
        assert "User" in repr_str
        assert str(user.id) in repr_str
        assert "test@example.com" in repr_str


class TestUserProperties:
    """Test user entity property access"""

    def test_properties_are_read_only(self):
        """Test that properties cannot be directly modified"""
        user = User(
            email="test@example.com",
            google_id="google_123",
        )

        # Properties should not have setters
        with pytest.raises(AttributeError):
            user.email = "new@example.com"

        with pytest.raises(AttributeError):
            user.id = uuid4()

        with pytest.raises(AttributeError):
            user.role = "admin"
