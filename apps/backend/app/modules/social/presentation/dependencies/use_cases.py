"""Social Module Use Case Dependencies.

FastAPI dependency functions that connect request-scope dependencies
with IoC container providers to create use case instances.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    pass
from app.modules.social.application.use_cases.cards.check_quota import (
    CheckUploadQuotaUseCase,
)
from app.modules.social.application.use_cases.cards.delete_card import DeleteCardUseCase
from app.modules.social.application.use_cases.cards.get_my_cards import (
    GetMyCardsUseCase,
)
from app.modules.social.application.use_cases.cards.upload_card import (
    UploadCardUseCase,
)
from app.modules.social.application.use_cases.chat.get_messages_use_case import (
    GetMessagesUseCase,
)
from app.modules.social.application.use_cases.chat.send_message_use_case import (
    SendMessageUseCase,
)
from app.modules.social.application.use_cases.friends.accept_friend_request_use_case import (
    AcceptFriendRequestUseCase,
)
from app.modules.social.application.use_cases.friends.block_user_use_case import (
    BlockUserUseCase,
)
from app.modules.social.application.use_cases.friends.send_friend_request_use_case import (
    SendFriendRequestUseCase,
)
from app.modules.social.application.use_cases.nearby.search_nearby_cards_use_case import (
    SearchNearbyCardsUseCase,
)
from app.modules.social.application.use_cases.nearby.update_user_location_use_case import (
    UpdateUserLocationUseCase,
)
from app.modules.social.application.use_cases.ratings.rate_user_use_case import (
    RateUserUseCase,
)
from app.modules.social.application.use_cases.reports.report_user_use_case import (
    ReportUserUseCase,
)
from app.modules.social.application.use_cases.trades.accept_trade_use_case import (
    AcceptTradeUseCase,
)
from app.modules.social.application.use_cases.trades.cancel_trade_use_case import (
    CancelTradeUseCase,
)
from app.modules.social.application.use_cases.trades.complete_trade_use_case import (
    CompleteTradeUseCase,
)
from app.modules.social.application.use_cases.trades.create_trade_proposal_use_case import (
    CreateTradeProposalUseCase,
)
from app.modules.social.application.use_cases.trades.get_trade_history_use_case import (
    GetTradeHistoryUseCase,
)
from app.modules.social.application.use_cases.trades.reject_trade_use_case import (
    RejectTradeUseCase,
)
from app.modules.social.domain.repositories.i_card_repository import ICardRepository
from app.modules.social.domain.repositories.i_chat_room_repository import (
    IChatRoomRepository,
)
from app.modules.social.domain.repositories.i_friendship_repository import (
    IFriendshipRepository,
)
from app.modules.social.domain.repositories.i_message_repository import (
    IMessageRepository,
)
from app.modules.social.domain.repositories.i_rating_repository import IRatingRepository
from app.modules.social.domain.repositories.i_report_repository import IReportRepository
from app.modules.social.domain.repositories.i_trade_repository import ITradeRepository
from app.shared.infrastructure.database.connection import get_db_session

# ========== Cards Use Cases ==========


@inject
def get_upload_card_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], ICardRepository] = Depends(
        Provide["social.card_repository"]
    ),
    use_case_factory: Callable[..., UploadCardUseCase] = Depends(
        Provide["social.upload_card_use_case_factory"]
    ),
) -> UploadCardUseCase:
    """Get UploadCardUseCase instance with request-scope dependencies."""
    card_repo = repo_factory(session)
    return use_case_factory(card_repository=card_repo)


@inject
def get_my_cards_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], ICardRepository] = Depends(
        Provide["social.card_repository"]
    ),
    use_case_factory: Callable[..., GetMyCardsUseCase] = Depends(
        Provide["social.get_my_cards_use_case_factory"]
    ),
) -> GetMyCardsUseCase:
    """Get GetMyCardsUseCase instance with request-scope dependencies."""
    card_repo = repo_factory(session)
    return use_case_factory(card_repository=card_repo)


@inject
def get_delete_card_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], ICardRepository] = Depends(
        Provide["social.card_repository"]
    ),
    use_case_factory: Callable[..., DeleteCardUseCase] = Depends(
        Provide["social.delete_card_use_case_factory"]
    ),
) -> DeleteCardUseCase:
    """Get DeleteCardUseCase instance with request-scope dependencies."""
    card_repo = repo_factory(session)
    return use_case_factory(card_repository=card_repo)


@inject
def get_check_quota_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], ICardRepository] = Depends(
        Provide["social.card_repository"]
    ),
    use_case_factory: Callable[..., CheckUploadQuotaUseCase] = Depends(
        Provide["social.check_quota_use_case_factory"]
    ),
) -> CheckUploadQuotaUseCase:
    """Get CheckUploadQuotaUseCase instance with request-scope dependencies."""
    card_repo = repo_factory(session)
    return use_case_factory(card_repository=card_repo)


# ========== Nearby Use Cases ==========


@inject
def get_search_nearby_cards_use_case(
    session: AsyncSession = Depends(get_db_session),
    card_repo_factory: Callable[[AsyncSession], ICardRepository] = Depends(
        Provide["social.card_repository"]
    ),
    use_case_factory: Callable[..., SearchNearbyCardsUseCase] = Depends(
        Provide["social.search_nearby_cards_use_case_factory"]
    ),
) -> SearchNearbyCardsUseCase:
    """Get SearchNearbyCardsUseCase instance with request-scope dependencies."""
    card_repo = card_repo_factory(session)
    return use_case_factory(card_repository=card_repo)


@inject
def get_update_user_location_use_case(
    session: AsyncSession = Depends(get_db_session),
    card_repo_factory: Callable[[AsyncSession], ICardRepository] = Depends(
        Provide["social.card_repository"]
    ),
    use_case_factory: Callable[..., UpdateUserLocationUseCase] = Depends(
        Provide["social.update_user_location_use_case_factory"]
    ),
) -> UpdateUserLocationUseCase:
    """Get UpdateUserLocationUseCase instance with request-scope dependencies."""
    card_repo = card_repo_factory(session)
    return use_case_factory(card_repository=card_repo)


# ========== Friends Use Cases ==========


@inject
def get_send_friend_request_use_case(
    session: AsyncSession = Depends(get_db_session),
    friendship_repo_factory: Callable[[AsyncSession], IFriendshipRepository] = Depends(
        Provide["social.friendship_repository"]
    ),
    use_case_factory: Callable[..., SendFriendRequestUseCase] = Depends(
        Provide["social.send_friend_request_use_case_factory"]
    ),
) -> SendFriendRequestUseCase:
    """Get SendFriendRequestUseCase instance with request-scope dependencies."""
    friendship_repo = friendship_repo_factory(session)
    return use_case_factory(friendship_repository=friendship_repo)


@inject
def get_accept_friend_request_use_case(
    session: AsyncSession = Depends(get_db_session),
    friendship_repo_factory: Callable[[AsyncSession], IFriendshipRepository] = Depends(
        Provide["social.friendship_repository"]
    ),
    use_case_factory: Callable[..., AcceptFriendRequestUseCase] = Depends(
        Provide["social.accept_friend_request_use_case_factory"]
    ),
) -> AcceptFriendRequestUseCase:
    """Get AcceptFriendRequestUseCase instance with request-scope dependencies."""
    friendship_repo = friendship_repo_factory(session)
    return use_case_factory(friendship_repository=friendship_repo)


@inject
def get_block_user_use_case(
    session: AsyncSession = Depends(get_db_session),
    friendship_repo_factory: Callable[[AsyncSession], IFriendshipRepository] = Depends(
        Provide["social.friendship_repository"]
    ),
    use_case_factory: Callable[..., BlockUserUseCase] = Depends(
        Provide["social.block_user_use_case_factory"]
    ),
) -> BlockUserUseCase:
    """Get BlockUserUseCase instance with request-scope dependencies."""
    friendship_repo = friendship_repo_factory(session)
    return use_case_factory(friendship_repository=friendship_repo)


# ========== Chat Use Cases ==========


@inject
def get_send_message_use_case(
    session: AsyncSession = Depends(get_db_session),
    chat_room_repo_factory: Callable[[AsyncSession], IChatRoomRepository] = Depends(
        Provide["social.chat_room_repository"]
    ),
    message_repo_factory: Callable[[AsyncSession], IMessageRepository] = Depends(
        Provide["social.message_repository"]
    ),
    use_case_factory: Callable[..., SendMessageUseCase] = Depends(
        Provide["social.send_message_use_case_factory"]
    ),
) -> SendMessageUseCase:
    """Get SendMessageUseCase instance with request-scope dependencies."""
    chat_room_repo = chat_room_repo_factory(session)
    message_repo = message_repo_factory(session)
    return use_case_factory(
        chat_room_repository=chat_room_repo, message_repository=message_repo
    )


# ========== Ratings Use Cases ==========


@inject
def get_rate_user_use_case(
    session: AsyncSession = Depends(get_db_session),
    rating_repo_factory: Callable[[AsyncSession], IRatingRepository] = Depends(
        Provide["social.rating_repository"]
    ),
    friendship_repo_factory: Callable[[AsyncSession], IFriendshipRepository] = Depends(
        Provide["social.friendship_repository"]
    ),
    use_case_factory: Callable[..., RateUserUseCase] = Depends(
        Provide["social.rate_user_use_case_factory"]
    ),
) -> RateUserUseCase:
    """Get RateUserUseCase instance with request-scope dependencies."""
    rating_repo = rating_repo_factory(session)
    friendship_repo = friendship_repo_factory(session)
    return use_case_factory(
        rating_repository=rating_repo, friendship_repository=friendship_repo
    )


# ========== Reports Use Cases ==========


@inject
def get_report_user_use_case(
    session: AsyncSession = Depends(get_db_session),
    report_repo_factory: Callable[[AsyncSession], IReportRepository] = Depends(
        Provide["social.report_repository"]
    ),
    use_case_factory: Callable[..., ReportUserUseCase] = Depends(
        Provide["social.report_user_use_case_factory"]
    ),
) -> ReportUserUseCase:
    """Get ReportUserUseCase instance with request-scope dependencies."""
    report_repo = report_repo_factory(session)
    return use_case_factory(report_repository=report_repo)


# ========== Trades Use Cases ==========


@inject
def get_create_trade_proposal_use_case(
    session: AsyncSession = Depends(get_db_session),
    trade_repo_factory: Callable[[AsyncSession], ITradeRepository] = Depends(
        Provide["social.trade_repository"]
    ),
    card_repo_factory: Callable[[AsyncSession], ICardRepository] = Depends(
        Provide["social.card_repository"]
    ),
    friendship_repo_factory: Callable[[AsyncSession], IFriendshipRepository] = Depends(
        Provide["social.friendship_repository"]
    ),
    use_case_factory: Callable[..., CreateTradeProposalUseCase] = Depends(
        Provide["social.create_trade_proposal_use_case_factory"]
    ),
) -> CreateTradeProposalUseCase:
    """Get CreateTradeProposalUseCase instance with request-scope dependencies."""
    trade_repo = trade_repo_factory(session)
    card_repo = card_repo_factory(session)
    friendship_repo = friendship_repo_factory(session)
    return use_case_factory(
        trade_repository=trade_repo,
        card_repository=card_repo,
        friendship_repository=friendship_repo,
    )


@inject
def get_accept_trade_use_case(
    session: AsyncSession = Depends(get_db_session),
    trade_repo_factory: Callable[[AsyncSession], ITradeRepository] = Depends(
        Provide["social.trade_repository"]
    ),
    card_repo_factory: Callable[[AsyncSession], ICardRepository] = Depends(
        Provide["social.card_repository"]
    ),
    chat_room_repo_factory: Callable[[AsyncSession], IChatRoomRepository] = Depends(
        Provide["social.chat_room_repository"]
    ),
    use_case_factory: Callable[..., AcceptTradeUseCase] = Depends(
        Provide["social.accept_trade_use_case_factory"]
    ),
) -> AcceptTradeUseCase:
    """Get AcceptTradeUseCase instance with request-scope dependencies."""
    trade_repo = trade_repo_factory(session)
    card_repo = card_repo_factory(session)
    chat_room_repo = chat_room_repo_factory(session)
    return use_case_factory(
        trade_repository=trade_repo,
        card_repository=card_repo,
        chat_room_repository=chat_room_repo,
    )


@inject
def get_cancel_trade_use_case(
    session: AsyncSession = Depends(get_db_session),
    trade_repo_factory: Callable[[AsyncSession], ITradeRepository] = Depends(
        Provide["social.trade_repository"]
    ),
    use_case_factory: Callable[..., CancelTradeUseCase] = Depends(
        Provide["social.cancel_trade_use_case_factory"]
    ),
) -> CancelTradeUseCase:
    """Get CancelTradeUseCase instance with request-scope dependencies."""
    trade_repo = trade_repo_factory(session)
    return use_case_factory(trade_repository=trade_repo)


# ========== Repository Dependencies ==========
# For simple queries that don't need use cases


@inject
def get_friendship_repository(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], IFriendshipRepository] = Depends(
        Provide["social.friendship_repository"]
    ),
) -> IFriendshipRepository:
    """Get IFriendshipRepository instance with request-scope dependencies."""
    return repo_factory(session)


@inject
def get_chat_room_repository(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], IChatRoomRepository] = Depends(
        Provide["social.chat_room_repository"]
    ),
) -> IChatRoomRepository:
    """Get IChatRoomRepository instance with request-scope dependencies."""
    return repo_factory(session)


@inject
def get_message_repository(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], IMessageRepository] = Depends(
        Provide["social.message_repository"]
    ),
) -> IMessageRepository:
    """Get IMessageRepository instance with request-scope dependencies."""
    return repo_factory(session)


# ========== Chat Use Cases (continued) ==========


@inject
def get_messages_use_case(
    session: AsyncSession = Depends(get_db_session),
    message_repo_factory: Callable[[AsyncSession], IMessageRepository] = Depends(
        Provide["social.message_repository"]
    ),
    use_case_factory: Callable[..., GetMessagesUseCase] = Depends(
        Provide["social.get_messages_use_case_factory"]
    ),
) -> GetMessagesUseCase:
    """Get GetMessagesUseCase instance with request-scope dependencies."""
    message_repo = message_repo_factory(session)
    return use_case_factory(message_repository=message_repo)


@inject
def get_reject_trade_use_case(
    session: AsyncSession = Depends(get_db_session),
    trade_repo_factory: Callable[[AsyncSession], ITradeRepository] = Depends(
        Provide["social.trade_repository"]
    ),
    use_case_factory: Callable[..., RejectTradeUseCase] = Depends(
        Provide["social.reject_trade_use_case_factory"]
    ),
) -> RejectTradeUseCase:
    """Get RejectTradeUseCase instance with request-scope dependencies."""
    trade_repo = trade_repo_factory(session)
    return use_case_factory(trade_repository=trade_repo)


@inject
def get_complete_trade_use_case(
    session: AsyncSession = Depends(get_db_session),
    trade_repo_factory: Callable[[AsyncSession], ITradeRepository] = Depends(
        Provide["social.trade_repository"]
    ),
    use_case_factory: Callable[..., CompleteTradeUseCase] = Depends(
        Provide["social.complete_trade_use_case_factory"]
    ),
) -> CompleteTradeUseCase:
    """Get CompleteTradeUseCase instance with request-scope dependencies."""
    trade_repo = trade_repo_factory(session)
    return use_case_factory(trade_repository=trade_repo)


@inject
def get_trade_history_use_case(
    session: AsyncSession = Depends(get_db_session),
    trade_repo_factory: Callable[[AsyncSession], ITradeRepository] = Depends(
        Provide["social.trade_repository"]
    ),
    use_case_factory: Callable[..., GetTradeHistoryUseCase] = Depends(
        Provide["social.get_trade_history_use_case_factory"]
    ),
) -> GetTradeHistoryUseCase:
    """Get GetTradeHistoryUseCase instance with request-scope dependencies."""
    trade_repo = trade_repo_factory(session)
    return use_case_factory(trade_repository=trade_repo)


@inject
def get_trade_repository(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], ITradeRepository] = Depends(
        Provide["social.trade_repository"]
    ),
) -> ITradeRepository:
    """Get ITradeRepository instance with request-scope dependencies."""
    return repo_factory(session)
