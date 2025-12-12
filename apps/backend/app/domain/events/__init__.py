"""Domain events"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class DomainEvent:
    """Base domain event"""
    occurred_at: datetime = None

    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.utcnow()


@dataclass
class UserRegisteredEvent(DomainEvent):
    """User registered event"""
    user_id: UUID
    email: str
    google_id: str


@dataclass
class ProfileUpdatedEvent(DomainEvent):
    """Profile updated event"""
    user_id: UUID
    fields_updated: list[str]


@dataclass
class PrivacySettingsChangedEvent(DomainEvent):
    """Privacy settings changed event"""
    user_id: UUID
    privacy_flags: dict[str, bool]
