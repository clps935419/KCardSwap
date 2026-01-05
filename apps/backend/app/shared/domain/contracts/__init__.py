"""
Shared Domain Contracts

Defines interfaces for cross-bounded-context communication.
These contracts allow modules to depend on abstractions rather than concrete implementations.
"""

from app.shared.domain.contracts.i_chat_room_service import IChatRoomService
from app.shared.domain.contracts.i_friendship_service import IFriendshipService
from app.shared.domain.contracts.i_profile_query_service import IProfileQueryService
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)
from app.shared.domain.contracts.i_user_basic_info_service import (
    IUserBasicInfoService,
)

__all__ = [
    "ISubscriptionQueryService",
    "IProfileQueryService",
    "IUserBasicInfoService",
    "IFriendshipService",
    "IChatRoomService",
]
