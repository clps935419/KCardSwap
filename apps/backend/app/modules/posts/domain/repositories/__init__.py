"""Domain repositories for Posts module"""

from .i_post_interest_repository import IPostInterestRepository
from .i_post_repository import IPostRepository

__all__ = [
    "IPostRepository",
    "IPostInterestRepository",
]
