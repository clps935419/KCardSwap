"""Social domain repositories"""
from .card_repository import ICardRepository
from .chat_room_repository import IChatRoomRepository
from .friendship_repository import IFriendshipRepository
from .message_repository import IMessageRepository
from .rating_repository import IRatingRepository
from .report_repository import IReportRepository

__all__ = [
    "ICardRepository",
    "IChatRoomRepository",
    "IFriendshipRepository",
    "IMessageRepository",
    "IRatingRepository",
    "IReportRepository",
]
