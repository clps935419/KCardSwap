"""
Unit tests for Profile Entity
Testing profile management, privacy settings, and location features
"""
from datetime import datetime
from uuid import UUID, uuid4

import pytest

from app.modules.identity.domain.entities.profile import Profile


class TestProfileCreation:
    """Test profile entity creation and initialization"""

    def test_create_minimal_profile(self):
        """Test creating a profile with only required fields"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        assert profile.user_id == user_id
        assert isinstance(profile.id, UUID)
        assert profile.nickname is None
        assert profile.avatar_url is None
        assert profile.bio is None
        assert profile.region is None
        assert profile.preferences == {}
        assert profile.privacy_flags == {
            "nearby_visible": True,
            "show_online": True,
            "allow_stranger_chat": True,
        }
        assert profile.last_lat is None
        assert profile.last_lng is None
        assert profile.stealth_mode is False
        assert isinstance(profile.created_at, datetime)
        assert isinstance(profile.updated_at, datetime)

    def test_create_full_profile(self):
        """Test creating a profile with all fields"""
        user_id = uuid4()
        profile_id = uuid4()
        now = datetime.utcnow()
        preferences = {"language": "zh-TW", "theme": "dark"}
        privacy_flags = {"nearby_visible": False, "show_online": False}

        profile = Profile(
            user_id=user_id,
            id=profile_id,
            nickname="TestUser",
            avatar_url="https://example.com/avatar.jpg",
            bio="Test bio",
            region="TW",
            preferences=preferences,
            privacy_flags=privacy_flags,
            last_lat=25.0330,
            last_lng=121.5654,
            stealth_mode=True,
            created_at=now,
            updated_at=now,
        )

        assert profile.id == profile_id
        assert profile.user_id == user_id
        assert profile.nickname == "TestUser"
        assert profile.avatar_url == "https://example.com/avatar.jpg"
        assert profile.bio == "Test bio"
        assert profile.region == "TW"
        assert profile.preferences == preferences
        assert profile.privacy_flags["nearby_visible"] is False
        assert profile.privacy_flags["show_online"] is False
        assert profile.last_lat == 25.0330
        assert profile.last_lng == 121.5654
        assert profile.stealth_mode is True
        assert profile.created_at == now
        assert profile.updated_at == now

    def test_default_privacy_flags(self):
        """Test that default privacy flags are set correctly"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        assert profile.privacy_flags["nearby_visible"] is True
        assert profile.privacy_flags["show_online"] is True
        assert profile.privacy_flags["allow_stranger_chat"] is True


class TestProfileValidation:
    """Test profile entity validation rules"""

    def test_nickname_too_long(self):
        """Test that nickname over 100 characters raises ValueError"""
        user_id = uuid4()
        long_nickname = "a" * 101

        with pytest.raises(ValueError, match="Nickname must be 100 characters or less"):
            Profile(user_id=user_id, nickname=long_nickname)

    def test_nickname_exactly_100_chars(self):
        """Test that nickname with exactly 100 characters is valid"""
        user_id = uuid4()
        nickname = "a" * 100

        profile = Profile(user_id=user_id, nickname=nickname)
        assert profile.nickname == nickname

    def test_bio_too_long(self):
        """Test that bio over 1000 characters raises ValueError"""
        user_id = uuid4()
        long_bio = "a" * 1001

        with pytest.raises(ValueError, match="Bio must be 1000 characters or less"):
            Profile(user_id=user_id, bio=long_bio)

    def test_bio_exactly_1000_chars(self):
        """Test that bio with exactly 1000 characters is valid"""
        user_id = uuid4()
        bio = "a" * 1000

        profile = Profile(user_id=user_id, bio=bio)
        assert profile.bio == bio

    def test_invalid_latitude_too_low(self):
        """Test that latitude below -90 raises ValueError"""
        user_id = uuid4()

        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            Profile(user_id=user_id, last_lat=-91.0, last_lng=0.0)

    def test_invalid_latitude_too_high(self):
        """Test that latitude above 90 raises ValueError"""
        user_id = uuid4()

        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            Profile(user_id=user_id, last_lat=91.0, last_lng=0.0)

    def test_valid_latitude_bounds(self):
        """Test that latitude at exact bounds is valid"""
        user_id = uuid4()

        profile1 = Profile(user_id=user_id, last_lat=-90.0, last_lng=0.0)
        assert profile1.last_lat == -90.0

        profile2 = Profile(user_id=uuid4(), last_lat=90.0, last_lng=0.0)
        assert profile2.last_lat == 90.0

    def test_invalid_longitude_too_low(self):
        """Test that longitude below -180 raises ValueError"""
        user_id = uuid4()

        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            Profile(user_id=user_id, last_lat=0.0, last_lng=-181.0)

    def test_invalid_longitude_too_high(self):
        """Test that longitude above 180 raises ValueError"""
        user_id = uuid4()

        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            Profile(user_id=user_id, last_lat=0.0, last_lng=181.0)

    def test_valid_longitude_bounds(self):
        """Test that longitude at exact bounds is valid"""
        user_id = uuid4()

        profile1 = Profile(user_id=user_id, last_lat=0.0, last_lng=-180.0)
        assert profile1.last_lng == -180.0

        profile2 = Profile(user_id=uuid4(), last_lat=0.0, last_lng=180.0)
        assert profile2.last_lng == 180.0


class TestProfileUpdate:
    """Test profile update methods"""

    def test_update_profile_all_fields(self):
        """Test updating all profile fields"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        old_updated_at = profile.updated_at
        new_preferences = {"language": "en-US"}

        profile.update_profile(
            nickname="NewName",
            avatar_url="https://example.com/new.jpg",
            bio="New bio",
            region="US",
            preferences=new_preferences,
        )

        assert profile.nickname == "NewName"
        assert profile.avatar_url == "https://example.com/new.jpg"
        assert profile.bio == "New bio"
        assert profile.region == "US"
        assert profile.preferences["language"] == "en-US"
        assert profile.updated_at > old_updated_at

    def test_update_profile_partial_fields(self):
        """Test updating only some profile fields"""
        user_id = uuid4()
        profile = Profile(
            user_id=user_id,
            nickname="Original",
            bio="Original bio",
        )

        profile.update_profile(nickname="Updated")

        assert profile.nickname == "Updated"
        assert profile.bio == "Original bio"  # Unchanged

    def test_update_profile_validates(self):
        """Test that update_profile validates new values"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        with pytest.raises(ValueError, match="Nickname must be 100 characters or less"):
            profile.update_profile(nickname="a" * 101)

    def test_update_preferences_merges(self):
        """Test that preferences are merged, not replaced"""
        user_id = uuid4()
        profile = Profile(
            user_id=user_id,
            preferences={"language": "zh-TW", "theme": "dark"},
        )

        profile.update_profile(preferences={"theme": "light", "font": "large"})

        assert profile.preferences["language"] == "zh-TW"  # Preserved
        assert profile.preferences["theme"] == "light"  # Updated
        assert profile.preferences["font"] == "large"  # Added


class TestPrivacySettings:
    """Test privacy settings methods"""

    def test_update_privacy_settings(self):
        """Test updating privacy settings"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        old_updated_at = profile.updated_at
        profile.update_privacy_settings({"nearby_visible": False})

        assert profile.privacy_flags["nearby_visible"] is False
        assert profile.privacy_flags["show_online"] is True  # Unchanged
        assert profile.updated_at > old_updated_at

    def test_is_nearby_visible(self):
        """Test is_nearby_visible method"""
        user_id = uuid4()

        profile1 = Profile(
            user_id=user_id,
            privacy_flags={"nearby_visible": True},
        )
        assert profile1.is_nearby_visible() is True

        profile2 = Profile(
            user_id=uuid4(),
            privacy_flags={"nearby_visible": False},
        )
        assert profile2.is_nearby_visible() is False

    def test_shows_online_status(self):
        """Test shows_online_status method"""
        user_id = uuid4()

        profile1 = Profile(
            user_id=user_id,
            privacy_flags={"show_online": True},
        )
        assert profile1.shows_online_status() is True

        profile2 = Profile(
            user_id=uuid4(),
            privacy_flags={"show_online": False},
        )
        assert profile2.shows_online_status() is False

    def test_allows_stranger_chat(self):
        """Test allows_stranger_chat method"""
        user_id = uuid4()

        profile1 = Profile(
            user_id=user_id,
            privacy_flags={"allow_stranger_chat": True},
        )
        assert profile1.allows_stranger_chat() is True

        profile2 = Profile(
            user_id=uuid4(),
            privacy_flags={"allow_stranger_chat": False},
        )
        assert profile2.allows_stranger_chat() is False

    def test_privacy_flags_default_values(self):
        """Test default values when privacy flag doesn't exist"""
        user_id = uuid4()
        profile = Profile(user_id=user_id, privacy_flags={})

        # Should return default True when key doesn't exist
        assert profile.is_nearby_visible() is True
        assert profile.shows_online_status() is True
        assert profile.allows_stranger_chat() is True


class TestLocationManagement:
    """Test location management methods"""

    def test_update_location_valid(self):
        """Test updating location with valid coordinates"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        old_updated_at = profile.updated_at
        profile.update_location(25.0330, 121.5654)

        assert profile.last_lat == 25.0330
        assert profile.last_lng == 121.5654
        assert profile.updated_at > old_updated_at

    def test_update_location_invalid_latitude(self):
        """Test that update_location validates latitude"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            profile.update_location(91.0, 0.0)

        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            profile.update_location(-91.0, 0.0)

    def test_update_location_invalid_longitude(self):
        """Test that update_location validates longitude"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            profile.update_location(0.0, 181.0)

        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            profile.update_location(0.0, -181.0)

    def test_has_location(self):
        """Test has_location method"""
        user_id = uuid4()

        profile1 = Profile(user_id=user_id)
        assert profile1.has_location() is False

        profile2 = Profile(user_id=uuid4(), last_lat=25.0, last_lng=121.0)
        assert profile2.has_location() is True

        profile3 = Profile(user_id=uuid4(), last_lat=25.0)
        assert profile3.has_location() is False

        profile4 = Profile(user_id=uuid4(), last_lng=121.0)
        assert profile4.has_location() is False

    def test_set_stealth_mode(self):
        """Test set_stealth_mode method"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        assert profile.stealth_mode is False

        old_updated_at = profile.updated_at
        profile.set_stealth_mode(True)

        assert profile.stealth_mode is True
        assert profile.updated_at > old_updated_at

        profile.set_stealth_mode(False)
        assert profile.stealth_mode is False


class TestProfileEquality:
    """Test profile entity equality and hashing"""

    def test_profiles_with_same_user_id_are_equal(self):
        """Test that profiles with same user_id are equal"""
        user_id = uuid4()

        profile1 = Profile(user_id=user_id, nickname="User1")
        profile2 = Profile(user_id=user_id, nickname="User2")

        assert profile1 == profile2

    def test_profiles_with_different_user_ids_are_not_equal(self):
        """Test that profiles with different user_ids are not equal"""
        profile1 = Profile(user_id=uuid4())
        profile2 = Profile(user_id=uuid4())

        assert profile1 != profile2

    def test_profile_not_equal_to_non_profile(self):
        """Test that profile is not equal to non-Profile object"""
        profile = Profile(user_id=uuid4())

        assert profile != "not a profile"
        assert profile != 123
        assert profile != None

    def test_profile_hash(self):
        """Test that profile can be hashed"""
        profile = Profile(user_id=uuid4())

        # Should not raise
        hash(profile)

        # Should be usable in sets
        profile_set = {profile}
        assert profile in profile_set

    def test_profile_repr(self):
        """Test profile string representation"""
        user_id = uuid4()
        profile = Profile(user_id=user_id, nickname="TestUser")

        repr_str = repr(profile)
        assert "Profile" in repr_str
        assert str(user_id) in repr_str
        assert "TestUser" in repr_str


class TestProfileProperties:
    """Test profile property access and immutability"""

    def test_properties_return_copies(self):
        """Test that preferences and privacy_flags return copies"""
        user_id = uuid4()
        original_prefs = {"language": "zh-TW"}
        original_privacy = {"nearby_visible": True}

        profile = Profile(
            user_id=user_id,
            preferences=original_prefs,
            privacy_flags=original_privacy,
        )

        # Modifying returned dict should not affect internal state
        returned_prefs = profile.preferences
        returned_prefs["new_key"] = "value"
        assert "new_key" not in profile.preferences

        returned_privacy = profile.privacy_flags
        returned_privacy["new_flag"] = False
        assert "new_flag" not in profile.privacy_flags

    def test_properties_are_read_only(self):
        """Test that properties cannot be directly modified"""
        user_id = uuid4()
        profile = Profile(user_id=user_id)

        # Properties should not have setters
        with pytest.raises(AttributeError):
            profile.nickname = "NewName"

        with pytest.raises(AttributeError):
            profile.user_id = uuid4()

        with pytest.raises(AttributeError):
            profile.stealth_mode = True
