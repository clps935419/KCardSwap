"""Domain repositories for Social module."""

from .i_card_repository import ICardRepository
from .i_chat_room_repository import IChatRoomRepository
from .i_friendship_repository import IFriendshipRepository
from .i_message_repository import IMessageRepository
from .i_report_repository import IReportRepository

__all__ = [
    "ICardRepository",
    "IChatRoomRepository",
    "IFriendshipRepository",
    "IMessageRepository",
    "IReportRepository",
]
