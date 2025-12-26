"""
Unit tests for Profile entity
"""
from uuid import uuid4

import pytest

from app.modules.identity.domain.entities.profile import Profile


def test_profile_creation():
    """Test profile entity creation"""
    user_id = uuid4()
    profile = Profile(user_id=user_id)

    assert profile.id is not None
    assert profile.user_id == user_id
    assert profile.nickname is None
    assert profile.privacy_flags["nearby_visible"] is True
    assert profile.privacy_flags["show_online"] is True
    assert profile.privacy_flags["allow_stranger_chat"] is True


def test_profile_with_data():
    """Test profile creation with data"""
    user_id = uuid4()
    profile = Profile(
        user_id=user_id,
        nickname="TestUser",
        bio="Test bio",
        region="Seoul"
    )

    assert profile.id is not None
    assert profile.nickname == "TestUser"
    assert profile.bio == "Test bio"
    assert profile.region == "Seoul"


def test_profile_validation_nickname_length():
    """Test nickname length validation"""
    user_id = uuid4()
    with pytest.raises(ValueError, match="Nickname must be 100 characters or less"):
        Profile(user_id=user_id, nickname="x" * 101)


def test_profile_validation_bio_length():
    """Test bio length validation"""
    user_id = uuid4()
    with pytest.raises(ValueError, match="Bio must be 1000 characters or less"):
        Profile(user_id=user_id, bio="x" * 1001)


def test_profile_update():
    """Test profile update"""
    user_id = uuid4()
    profile = Profile(user_id=user_id)

    profile.update_profile(
        nickname="NewNick",
        bio="New bio",
        region="Busan"
    )

    assert profile.nickname == "NewNick"
    assert profile.bio == "New bio"
    assert profile.region == "Busan"


def test_profile_privacy_settings():
    """Test privacy settings update"""
    user_id = uuid4()
    profile = Profile(user_id=user_id)

    profile.update_privacy_settings({
        "nearby_visible": False,
        "show_online": False
    })

    assert profile.is_nearby_visible() is False
    assert profile.shows_online_status() is False
    assert profile.allows_stranger_chat() is True  # Not updated, should remain True
