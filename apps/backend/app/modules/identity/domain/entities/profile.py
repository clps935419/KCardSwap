"""
Profile Entity - User profile information
Following DDD principles: No framework dependencies
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID


class Profile:
    """
    Profile entity representing user profile data and privacy settings.
    """

    def __init__(
        self,
        user_id: UUID,
        id: Optional[UUID] = None,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        region: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        privacy_flags: Optional[Dict[str, bool]] = None,
        last_lat: Optional[float] = None,
        last_lng: Optional[float] = None,
        stealth_mode: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = id or uuid.uuid4()
        self._user_id = user_id
        self._nickname = nickname
        self._avatar_url = avatar_url
        self._bio = bio
        self._region = region
        self._preferences = preferences or {}
        self._privacy_flags = privacy_flags or {
            "show_online": True,
            "allow_stranger_chat": True,
        }
        self._last_lat = last_lat
        self._last_lng = last_lng
        self._stealth_mode = stealth_mode
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

        self._validate()

    def _validate(self):
        """Validate profile data"""
        if self._nickname and len(self._nickname) > 100:
            raise ValueError("Nickname must be 100 characters or less")
        if self._bio and len(self._bio) > 1000:
            raise ValueError("Bio must be 1000 characters or less")

        # Validate coordinates if provided
        if self._last_lat is not None:
            if not -90 <= self._last_lat <= 90:
                raise ValueError("Latitude must be between -90 and 90")
        if self._last_lng is not None:
            if not -180 <= self._last_lng <= 180:
                raise ValueError("Longitude must be between -180 and 180")

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def nickname(self) -> Optional[str]:
        return self._nickname

    @property
    def avatar_url(self) -> Optional[str]:
        return self._avatar_url

    @property
    def bio(self) -> Optional[str]:
        return self._bio

    @property
    def region(self) -> Optional[str]:
        return self._region

    @property
    def preferences(self) -> Dict[str, Any]:
        return self._preferences.copy()

    @property
    def privacy_flags(self) -> Dict[str, bool]:
        return self._privacy_flags.copy()

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def last_lat(self) -> Optional[float]:
        return self._last_lat

    @property
    def last_lng(self) -> Optional[float]:
        return self._last_lng

    @property
    def stealth_mode(self) -> bool:
        return self._stealth_mode

    def update_profile(
        self,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        region: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ):
        """Update profile fields"""
        if nickname is not None:
            self._nickname = nickname
        if avatar_url is not None:
            self._avatar_url = avatar_url
        if bio is not None:
            self._bio = bio
        if region is not None:
            self._region = region
        if preferences is not None:
            self._preferences.update(preferences)

        self._updated_at = datetime.utcnow()
        self._validate()

    def update_privacy_settings(self, privacy_flags: Dict[str, bool]):
        """Update privacy settings"""
        self._privacy_flags.update(privacy_flags)
        self._updated_at = datetime.utcnow()

    def shows_online_status(self) -> bool:
        """Check if user shows online status"""
        return self._privacy_flags.get("show_online", True)

    def allows_stranger_chat(self) -> bool:
        """Check if user allows strangers to chat"""
        return self._privacy_flags.get("allow_stranger_chat", True)

    def update_location(self, lat: float, lng: float):
        """Update user's location"""
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= lng <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        self._last_lat = lat
        self._last_lng = lng
        self._updated_at = datetime.utcnow()

    def set_stealth_mode(self, enabled: bool):
        """Enable or disable stealth mode"""
        self._stealth_mode = enabled
        self._updated_at = datetime.utcnow()

    def has_location(self) -> bool:
        """Check if user has location set"""
        return self._last_lat is not None and self._last_lng is not None

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return self._user_id == other._user_id

    def __hash__(self):
        return hash(self._user_id)

    def __repr__(self):
        return f"Profile(user_id={self._user_id}, nickname={self._nickname})"
