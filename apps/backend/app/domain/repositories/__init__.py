"""Domain repository interfaces"""
from .profile_repository_interface import IProfileRepository
from .user_repository_interface import IUserRepository

__all__ = ["IUserRepository", "IProfileRepository"]
