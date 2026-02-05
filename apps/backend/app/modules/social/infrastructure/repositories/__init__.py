"""Social infrastructure repositories"""

from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.message_repository_impl import (
    MessageRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.report_repository_impl import (
    ReportRepositoryImpl,
)

__all__ = [
    "FriendshipRepositoryImpl",
    "ChatRoomRepositoryImpl",
    "MessageRepositoryImpl",
    "ReportRepositoryImpl",
]
