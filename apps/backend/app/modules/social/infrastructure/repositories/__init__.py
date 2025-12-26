"""Social infrastructure repositories"""

from app.modules.social.infrastructure.repositories.card_repository_impl import (
    CardRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.message_repository_impl import (
    MessageRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.rating_repository_impl import (
    RatingRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.report_repository_impl import (
    ReportRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.trade_repository_impl import (
    TradeRepositoryImpl,
)

__all__ = [
    "CardRepositoryImpl",
    "FriendshipRepositoryImpl",
    "ChatRoomRepositoryImpl",
    "MessageRepositoryImpl",
    "RatingRepositoryImpl",
    "ReportRepositoryImpl",
    "TradeRepositoryImpl",
]
