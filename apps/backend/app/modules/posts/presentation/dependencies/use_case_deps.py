"""
Use Case Dependencies for Posts Module using python-injector
"""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.application.use_cases.accept_interest_use_case import (
    AcceptInterestUseCase,
)
from app.modules.posts.application.use_cases.close_post_use_case import (
    ClosePostUseCase,
)
from app.modules.posts.application.use_cases.create_post_use_case import (
    CreatePostUseCase,
)
from app.modules.posts.application.use_cases.express_interest_use_case import (
    ExpressInterestUseCase,
)
from app.modules.posts.application.use_cases.list_board_posts_use_case import (
    ListBoardPostsUseCase,
)
from app.modules.posts.application.use_cases.list_post_interests_use_case import (
    ListPostInterestsUseCase,
)
from app.modules.posts.application.use_cases.reject_interest_use_case import (
    RejectInterestUseCase,
)
from app.shared.infrastructure.database.connection import get_db_session


def _get_injector(request: Request):
    """Get injector from app state."""
    return request.app.state.injector


async def get_create_post_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> CreatePostUseCase:
    """Get CreatePostUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(CreatePostUseCase)


async def get_list_board_posts_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> ListBoardPostsUseCase:
    """Get ListBoardPostsUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(ListBoardPostsUseCase)


async def get_express_interest_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> ExpressInterestUseCase:
    """Get ExpressInterestUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(ExpressInterestUseCase)


async def get_accept_interest_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> AcceptInterestUseCase:
    """Get AcceptInterestUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(AcceptInterestUseCase)


async def get_reject_interest_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> RejectInterestUseCase:
    """Get RejectInterestUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(RejectInterestUseCase)


async def get_close_post_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> ClosePostUseCase:
    """Get ClosePostUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(ClosePostUseCase)


async def get_list_post_interests_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> ListPostInterestsUseCase:
    """Get ListPostInterestsUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(ListPostInterestsUseCase)
