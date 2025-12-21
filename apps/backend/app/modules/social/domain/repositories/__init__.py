"""Social domain repositories"""
from .card_repository import CardRepository
from .chat_room_repository import ChatRoomRepository
from .friendship_repository import FriendshipRepository
from .message_repository import MessageRepository
from .rating_repository import RatingRepository
from .report_repository import ReportRepository

__all__ = [
    "CardRepository",
    "ChatRoomRepository",
    "FriendshipRepository",
    "MessageRepository",
    "RatingRepository",
    "ReportRepository",
]
