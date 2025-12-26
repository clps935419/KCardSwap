"""
Unit tests for User entity
"""
import pytest
from datetime import datetime
from uuid import uuid4

from app.modules.identity.domain.entities.user import User


def test_user_creation():
    """Test user entity creation"""
    google_id = "google123"
    email = "test@example.com"

    user = User(google_id=google_id, email=email)

    assert user.google_id == google_id
    assert user.email == email.lower()  # Email should be normalized
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_email_normalization():
    """Test email normalization"""
    user = User(google_id="google123", email="Test@Example.COM")
    assert user.email == "test@example.com"


def test_user_validation_empty_google_id():
    """Test validation fails for empty google_id"""
    with pytest.raises(
        ValueError, match="Either google_id or password_hash must be provided"
    ):
        User(google_id="", email="test@example.com")


def test_user_validation_invalid_email():
    """Test validation fails for invalid email"""
    with pytest.raises(ValueError, match="Invalid email format"):
        User(google_id="google123", email="invalid-email")


def test_user_equality():
    """Test user equality based on ID"""
    user_id = uuid4()
    user1 = User(id=user_id, google_id="google123", email="test@example.com")
    user2 = User(id=user_id, google_id="google456", email="other@example.com")
    user3 = User(google_id="google123", email="test@example.com")

    assert user1 == user2  # Same ID
    assert user1 != user3  # Different ID


def test_user_update_email():
    """Test updating user email"""
    user = User(google_id="google123", email="old@example.com")
    original_updated_at = user.updated_at

    user.update_email("NEW@Example.COM")

    assert user.email == "new@example.com"
    assert user.updated_at > original_updated_at
