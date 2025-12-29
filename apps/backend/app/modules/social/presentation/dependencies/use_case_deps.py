"""
Use Case Dependencies for Social Module using python-injector
"""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.application.use_cases.cards.check_quota import (
    CheckQuotaUseCase,
)
from app.modules.social.application.use_cases.cards.delete_card import (
    DeleteCardUseCase,
)
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
from app.shared.infrastructure.database.connection import get_db_session


def _get_injector(request: Request):
    """Get injector from app state."""
    return request.app.state.injector


# Card Use Case Dependencies
async def get_upload_card_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> UploadCardUseCase:
    """Get UploadCardUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(UploadCardUseCase)


async def get_get_my_cards_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> GetMyCardsUseCase:
    """Get GetMyCardsUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(GetMyCardsUseCase)


async def get_delete_card_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> DeleteCardUseCase:
    """Get DeleteCardUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(DeleteCardUseCase)


async def get_check_quota_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> CheckQuotaUseCase:
    """Get CheckQuotaUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(CheckQuotaUseCase)


# Nearby Use Case Dependencies
async def get_search_nearby_cards_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> SearchNearbyCardsUseCase:
    """Get SearchNearbyCardsUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(SearchNearbyCardsUseCase)


async def get_update_user_location_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> UpdateUserLocationUseCase:
    """Get UpdateUserLocationUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(UpdateUserLocationUseCase)


# Friend Use Case Dependencies
async def get_send_friend_request_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> SendFriendRequestUseCase:
    """Get SendFriendRequestUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(SendFriendRequestUseCase)


async def get_accept_friend_request_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> AcceptFriendRequestUseCase:
    """Get AcceptFriendRequestUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(AcceptFriendRequestUseCase)


async def get_block_user_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> BlockUserUseCase:
    """Get BlockUserUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(BlockUserUseCase)


# Chat Use Case Dependencies
async def get_send_message_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> SendMessageUseCase:
    """Get SendMessageUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(SendMessageUseCase)


async def get_get_messages_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> GetMessagesUseCase:
    """Get GetMessagesUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(GetMessagesUseCase)


# Rating Use Case Dependencies
async def get_rate_user_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> RateUserUseCase:
    """Get RateUserUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(RateUserUseCase)


# Report Use Case Dependencies
async def get_report_user_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> ReportUserUseCase:
    """Get ReportUserUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(ReportUserUseCase)


# Trade Use Case Dependencies
async def get_create_trade_proposal_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> CreateTradeProposalUseCase:
    """Get CreateTradeProposalUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(CreateTradeProposalUseCase)


async def get_accept_trade_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> AcceptTradeUseCase:
    """Get AcceptTradeUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(AcceptTradeUseCase)


async def get_reject_trade_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> RejectTradeUseCase:
    """Get RejectTradeUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(RejectTradeUseCase)


async def get_cancel_trade_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> CancelTradeUseCase:
    """Get CancelTradeUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(CancelTradeUseCase)


async def get_complete_trade_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> CompleteTradeUseCase:
    """Get CompleteTradeUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(CompleteTradeUseCase)


async def get_get_trade_history_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> GetTradeHistoryUseCase:
    """Get GetTradeHistoryUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(GetTradeHistoryUseCase)
