"""Social infrastructure repositories"""

from app.modules.social.infrastructure.repositories.card_repository_impl import (
    CardRepositoryImpl,
    SQLAlchemyCardRepository,
)
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
    SQLAlchemyChatRoomRepository,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
    SQLAlchemyFriendshipRepository,
)
from app.modules.social.infrastructure.repositories.message_repository_impl import (
    MessageRepositoryImpl,
    SQLAlchemyMessageRepository,
)
from app.modules.social.infrastructure.repositories.rating_repository_impl import (
    RatingRepositoryImpl,
    SQLAlchemyRatingRepository,
)
from app.modules.social.infrastructure.repositories.report_repository_impl import (
    ReportRepositoryImpl,
    SQLAlchemyReportRepository,
)

__all__ = [
    "CardRepositoryImpl",
    "SQLAlchemyCardRepository",
    "FriendshipRepositoryImpl",
    "SQLAlchemyFriendshipRepository",
    "ChatRoomRepositoryImpl",
    "SQLAlchemyChatRoomRepository",
    "MessageRepositoryImpl",
    "SQLAlchemyMessageRepository",
    "RatingRepositoryImpl",
    "SQLAlchemyRatingRepository",
    "ReportRepositoryImpl",
    "SQLAlchemyReportRepository",
]
