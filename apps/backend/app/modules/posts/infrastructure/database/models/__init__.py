"""Posts module database models"""

from .post_interest_model import PostInterestModel
from .post_like_model import PostLikeModel
from .post_model import PostModel

__all__ = [
    "PostModel",
    "PostLikeModel",
    "PostInterestModel",
]
