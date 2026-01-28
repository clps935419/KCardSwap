"""
Use Case Dependencies for Identity Module using python-injector
"""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.application.use_cases.auth.admin_login import (
    AdminLoginUseCase,
)
from app.modules.identity.application.use_cases.auth.google_callback import (
    GoogleCallbackUseCase,
)
from app.modules.identity.application.use_cases.auth.login_with_google import (
    GoogleLoginUseCase,
)
from app.modules.identity.application.use_cases.auth.login_with_google_code import (
    GoogleCodeLoginUseCase,
)
from app.modules.identity.application.use_cases.auth.logout import LogoutUseCase
from app.modules.identity.application.use_cases.auth.refresh_token import (
    RefreshTokenUseCase,
)
from app.modules.identity.application.use_cases.profile.get_profile import (
    GetProfileUseCase,
)
from app.modules.identity.application.use_cases.profile.update_profile import (
    UpdateProfileUseCase,
)
from app.modules.identity.application.use_cases.subscription.check_subscription_status_use_case import (
    CheckSubscriptionStatusUseCase,
)
from app.modules.identity.application.use_cases.subscription.expire_subscriptions_use_case import (
    ExpireSubscriptionsUseCase,
)
from app.modules.identity.application.use_cases.subscription.verify_receipt_use_case import (
    VerifyReceiptUseCase,
)
from app.shared.infrastructure.database.connection import get_db_session


def _get_injector(request: Request):
    """Get injector from app state."""
    return request.app.state.injector


# Auth Use Case Dependencies
async def get_google_login_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> GoogleLoginUseCase:
    """Get GoogleLoginUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(GoogleLoginUseCase)


async def get_google_callback_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> GoogleCallbackUseCase:
    """Get GoogleCallbackUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(GoogleCallbackUseCase)


async def get_google_code_login_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> GoogleCodeLoginUseCase:
    """Get GoogleCodeLoginUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(GoogleCodeLoginUseCase)


async def get_refresh_token_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> RefreshTokenUseCase:
    """Get RefreshTokenUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(RefreshTokenUseCase)


async def get_logout_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> LogoutUseCase:
    """Get LogoutUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(LogoutUseCase)


async def get_admin_login_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> AdminLoginUseCase:
    """Get AdminLoginUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(AdminLoginUseCase)


# Profile Use Case Dependencies
async def get_get_profile_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> GetProfileUseCase:
    """Get GetProfileUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(GetProfileUseCase)


async def get_update_profile_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> UpdateProfileUseCase:
    """Get UpdateProfileUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(UpdateProfileUseCase)


# Subscription Use Case Dependencies
async def get_verify_receipt_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> VerifyReceiptUseCase:
    """Get VerifyReceiptUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(VerifyReceiptUseCase)


async def get_check_subscription_status_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> CheckSubscriptionStatusUseCase:
    """Get CheckSubscriptionStatusUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(CheckSubscriptionStatusUseCase)


async def get_expire_subscriptions_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request = None,
) -> ExpireSubscriptionsUseCase:
    """Get ExpireSubscriptionsUseCase from injector with request-scoped session."""
    injector = _get_injector(request)
    child = injector.create_child_injector()
    child.binder.bind(AsyncSession, to=session)
    return child.get(ExpireSubscriptionsUseCase)
