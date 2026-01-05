"""
Social Module Application Services

Implements shared contracts for cross-bounded-context communication.
"""

from app.modules.social.application.services.chat_room_service_impl import (
    ChatRoomServiceImpl,
)
from app.modules.social.application.services.friendship_service_impl import (
    FriendshipServiceImpl,
)

__all__ = [
    "FriendshipServiceImpl",
    "ChatRoomServiceImpl",
]
