"""Social domain repositories"""
from .i_card_repository import ICardRepository
from .i_chat_room_repository import IChatRoomRepository
from .i_friendship_repository import IFriendshipRepository
from .i_message_repository import IMessageRepository
from .i_rating_repository import IRatingRepository
from .i_report_repository import IReportRepository
from .i_trade_repository import ITradeRepository

__all__ = [
    "ICardRepository",
    "IChatRoomRepository",
    "IFriendshipRepository",
    "IMessageRepository",
    "IRatingRepository",
    "IReportRepository",
    "ITradeRepository",
]
