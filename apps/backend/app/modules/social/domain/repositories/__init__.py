"""Domain repositories for Social module."""

from .i_chat_room_repository import IChatRoomRepository
from .i_friendship_repository import IFriendshipRepository
from .i_message_repository import IMessageRepository
from .i_report_repository import IReportRepository

__all__ = [
    "IChatRoomRepository",
    "IFriendshipRepository",
    "IMessageRepository",
    "IReportRepository",
]
