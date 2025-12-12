"""Domain repository interfaces"""
from .user_repository import IUserRepository
from .profile_repository import IProfileRepository

__all__ = ["IUserRepository", "IProfileRepository"]
