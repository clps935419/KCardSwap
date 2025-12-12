"""
Profile Entity - User profile information
Following DDD principles: No framework dependencies
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class Profile:
    """
    Profile entity representing user profile data and privacy settings.
    """
    
    def __init__(
        self,
        user_id: UUID,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        region: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        privacy_flags: Optional[Dict[str, bool]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._user_id = user_id
        self._nickname = nickname
        self._avatar_url = avatar_url
        self._bio = bio
        self._region = region
        self._preferences = preferences or {}
        self._privacy_flags = privacy_flags or {
            "nearby_visible": True,
            "show_online": True,
            "allow_stranger_chat": True
        }
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        
        self._validate()
    
    def _validate(self):
        """Validate profile data"""
        if self._nickname and len(self._nickname) > 100:
            raise ValueError("Nickname must be 100 characters or less")
        if self._bio and len(self._bio) > 1000:
            raise ValueError("Bio must be 1000 characters or less")
    
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
    
    def update_profile(
        self,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        region: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
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
    
    def is_nearby_visible(self) -> bool:
        """Check if user is visible in nearby search"""
        return self._privacy_flags.get("nearby_visible", True)
    
    def shows_online_status(self) -> bool:
        """Check if user shows online status"""
        return self._privacy_flags.get("show_online", True)
    
    def allows_stranger_chat(self) -> bool:
        """Check if user allows strangers to chat"""
        return self._privacy_flags.get("allow_stranger_chat", True)
    
    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return self._user_id == other._user_id
    
    def __hash__(self):
        return hash(self._user_id)
    
    def __repr__(self):
        return f"Profile(user_id={self._user_id}, nickname={self._nickname})"
