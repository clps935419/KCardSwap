"""
User Entity - Core domain model for users
Following DDD principles: No framework dependencies, pure business logic
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class User:
    """
    User entity representing a platform user.
    Contains core user information and business logic.
    """

    def __init__(
        self,
        email: str,
        google_id: Optional[str] = None,
        password_hash: Optional[str] = None,
        role: str = "user",
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = id or uuid4()
        self._google_id = google_id
        self._email = email.lower()  # Normalize email
        self._password_hash = password_hash
        self._role = role
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

        self._validate()

    def _validate(self):
        """Validate user data"""
        if not self._email or "@" not in self._email:
            raise ValueError("Invalid email format")
        # Either google_id or password_hash must be set
        if not self._google_id and not self._password_hash:
            raise ValueError("Either google_id or password_hash must be provided")
        # Role validation
        if self._role not in ["user", "admin", "super_admin"]:
            raise ValueError("Invalid role. Must be 'user', 'admin', or 'super_admin'")

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def google_id(self) -> str:
        return self._google_id

    @property
    def email(self) -> str:
        return self._email

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def password_hash(self) -> Optional[str]:
        return self._password_hash

    @property
    def role(self) -> str:
        return self._role

    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self._role in ["admin", "super_admin"]

    def update_email(self, new_email: str):
        """Update user email"""
        self._email = new_email.lower()
        self._updated_at = datetime.utcnow()
        self._validate()

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"User(id={self._id}, email={self._email})"
