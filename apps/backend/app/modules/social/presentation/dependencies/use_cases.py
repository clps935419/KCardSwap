"""Social Module Use Case Dependencies.

FastAPI dependency functions that connect request-scope dependencies
with IoC container providers to create use case instances.
"""

from collections.abc import Callable

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.container import container
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
from app.modules.social.application.use_cases.trades.create_trade_proposal_use_case import (
    CreateTradeProposalUseCase,
)
from app.modules.social.domain.repositories.card_repository import CardRepository
from app.modules.social.domain.repositories.chat_room_repository import (
    ChatRoomRepository,
)
from app.modules.social.domain.repositories.friendship_repository import (
    FriendshipRepository,
)
from app.modules.social.domain.repositories.message_repository import MessageRepository
from app.modules.social.domain.repositories.rating_repository import RatingRepository
from app.modules.social.domain.repositories.report_repository import ReportRepository
from app.modules.social.domain.repositories.trade_repository import TradeRepository
from app.shared.infrastructure.database.connection import get_db_session


# ========== Cards Use Cases ==========


@inject
def get_upload_card_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], CardRepository] = Provide[
        container.social.card_repository
    ],
    use_case_factory: Callable[..., UploadCardUseCase] = Provide[
        container.social.upload_card_use_case_factory
    ],
) -> UploadCardUseCase:
    """Get UploadCardUseCase instance with request-scope dependencies."""
    card_repo = repo_factory(session)
    return use_case_factory(card_repository=card_repo)


@inject
def get_my_cards_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], CardRepository] = Provide[
        container.social.card_repository
    ],
    use_case_factory: Callable[..., GetMyCardsUseCase] = Provide[
        container.social.get_my_cards_use_case_factory
    ],
) -> GetMyCardsUseCase:
    """Get GetMyCardsUseCase instance with request-scope dependencies."""
    card_repo = repo_factory(session)
    return use_case_factory(card_repository=card_repo)


@inject
def get_delete_card_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], CardRepository] = Provide[
        container.social.card_repository
    ],
    use_case_factory: Callable[..., DeleteCardUseCase] = Provide[
        container.social.delete_card_use_case_factory
    ],
) -> DeleteCardUseCase:
    """Get DeleteCardUseCase instance with request-scope dependencies."""
    card_repo = repo_factory(session)
    return use_case_factory(card_repository=card_repo)


@inject
def get_check_quota_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], CardRepository] = Provide[
        container.social.card_repository
    ],
    use_case_factory: Callable[..., CheckUploadQuotaUseCase] = Provide[
        container.social.check_quota_use_case_factory
    ],
) -> CheckUploadQuotaUseCase:
    """Get CheckUploadQuotaUseCase instance with request-scope dependencies."""
    card_repo = repo_factory(session)
    return use_case_factory(card_repository=card_repo)


# ========== Nearby Use Cases ==========


@inject
def get_search_nearby_cards_use_case(
    session: AsyncSession = Depends(get_db_session),
    card_repo_factory: Callable[[AsyncSession], CardRepository] = Provide[
        container.social.card_repository
    ],
    use_case_factory: Callable[..., SearchNearbyCardsUseCase] = Provide[
        container.social.search_nearby_cards_use_case_factory
    ],
) -> SearchNearbyCardsUseCase:
    """Get SearchNearbyCardsUseCase instance with request-scope dependencies."""
    card_repo = card_repo_factory(session)
    return use_case_factory(card_repository=card_repo)


@inject
def get_update_user_location_use_case(
    session: AsyncSession = Depends(get_db_session),
    card_repo_factory: Callable[[AsyncSession], CardRepository] = Provide[
        container.social.card_repository
    ],
    use_case_factory: Callable[..., UpdateUserLocationUseCase] = Provide[
        container.social.update_user_location_use_case_factory
    ],
) -> UpdateUserLocationUseCase:
    """Get UpdateUserLocationUseCase instance with request-scope dependencies."""
    card_repo = card_repo_factory(session)
    return use_case_factory(card_repository=card_repo)


# ========== Friends Use Cases ==========


@inject
def get_send_friend_request_use_case(
    session: AsyncSession = Depends(get_db_session),
    friendship_repo_factory: Callable[[AsyncSession], FriendshipRepository] = Provide[
        container.social.friendship_repository
    ],
    use_case_factory: Callable[..., SendFriendRequestUseCase] = Provide[
        container.social.send_friend_request_use_case_factory
    ],
) -> SendFriendRequestUseCase:
    """Get SendFriendRequestUseCase instance with request-scope dependencies."""
    friendship_repo = friendship_repo_factory(session)
    return use_case_factory(friendship_repository=friendship_repo)


@inject
def get_accept_friend_request_use_case(
    session: AsyncSession = Depends(get_db_session),
    friendship_repo_factory: Callable[[AsyncSession], FriendshipRepository] = Provide[
        container.social.friendship_repository
    ],
    use_case_factory: Callable[..., AcceptFriendRequestUseCase] = Provide[
        container.social.accept_friend_request_use_case_factory
    ],
) -> AcceptFriendRequestUseCase:
    """Get AcceptFriendRequestUseCase instance with request-scope dependencies."""
    friendship_repo = friendship_repo_factory(session)
    return use_case_factory(friendship_repository=friendship_repo)


@inject
def get_block_user_use_case(
    session: AsyncSession = Depends(get_db_session),
    friendship_repo_factory: Callable[[AsyncSession], FriendshipRepository] = Provide[
        container.social.friendship_repository
    ],
    use_case_factory: Callable[..., BlockUserUseCase] = Provide[
        container.social.block_user_use_case_factory
    ],
) -> BlockUserUseCase:
    """Get BlockUserUseCase instance with request-scope dependencies."""
    friendship_repo = friendship_repo_factory(session)
    return use_case_factory(friendship_repository=friendship_repo)


# ========== Chat Use Cases ==========


@inject
def get_send_message_use_case(
    session: AsyncSession = Depends(get_db_session),
    chat_room_repo_factory: Callable[[AsyncSession], ChatRoomRepository] = Provide[
        container.social.chat_room_repository
    ],
    message_repo_factory: Callable[[AsyncSession], MessageRepository] = Provide[
        container.social.message_repository
    ],
    use_case_factory: Callable[..., SendMessageUseCase] = Provide[
        container.social.send_message_use_case_factory
    ],
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
    rating_repo_factory: Callable[[AsyncSession], RatingRepository] = Provide[
        container.social.rating_repository
    ],
    friendship_repo_factory: Callable[[AsyncSession], FriendshipRepository] = Provide[
        container.social.friendship_repository
    ],
    use_case_factory: Callable[..., RateUserUseCase] = Provide[
        container.social.rate_user_use_case_factory
    ],
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
    report_repo_factory: Callable[[AsyncSession], ReportRepository] = Provide[
        container.social.report_repository
    ],
    use_case_factory: Callable[..., ReportUserUseCase] = Provide[
        container.social.report_user_use_case_factory
    ],
) -> ReportUserUseCase:
    """Get ReportUserUseCase instance with request-scope dependencies."""
    report_repo = report_repo_factory(session)
    return use_case_factory(report_repository=report_repo)


# ========== Trades Use Cases ==========


@inject
def get_create_trade_proposal_use_case(
    session: AsyncSession = Depends(get_db_session),
    trade_repo_factory: Callable[[AsyncSession], TradeRepository] = Provide[
        container.social.trade_repository
    ],
    card_repo_factory: Callable[[AsyncSession], CardRepository] = Provide[
        container.social.card_repository
    ],
    friendship_repo_factory: Callable[[AsyncSession], FriendshipRepository] = Provide[
        container.social.friendship_repository
    ],
    use_case_factory: Callable[..., CreateTradeProposalUseCase] = Provide[
        container.social.create_trade_proposal_use_case_factory
    ],
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
    trade_repo_factory: Callable[[AsyncSession], TradeRepository] = Provide[
        container.social.trade_repository
    ],
    card_repo_factory: Callable[[AsyncSession], CardRepository] = Provide[
        container.social.card_repository
    ],
    chat_room_repo_factory: Callable[[AsyncSession], ChatRoomRepository] = Provide[
        container.social.chat_room_repository
    ],
    use_case_factory: Callable[..., AcceptTradeUseCase] = Provide[
        container.social.accept_trade_use_case_factory
    ],
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
    trade_repo_factory: Callable[[AsyncSession], TradeRepository] = Provide[
        container.social.trade_repository
    ],
    use_case_factory: Callable[..., CancelTradeUseCase] = Provide[
        container.social.cancel_trade_use_case_factory
    ],
) -> CancelTradeUseCase:
    """Get CancelTradeUseCase instance with request-scope dependencies."""
    trade_repo = trade_repo_factory(session)
    return use_case_factory(trade_repository=trade_repo)
