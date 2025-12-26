"""Identity Module Use Case Dependencies.

FastAPI dependency functions that connect request-scope dependencies
with IoC container providers to create use case instances.
"""

from collections.abc import Callable

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
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
from app.modules.identity.domain.repositories.profile_repository import (
    IProfileRepository,
)
from app.modules.identity.domain.repositories.purchase_token_repository import (
    PurchaseTokenRepository,
)
from app.modules.identity.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.modules.identity.domain.repositories.subscription_repository import (
    SubscriptionRepository,
)
from app.modules.identity.domain.repositories.user_repository import IUserRepository
from app.shared.infrastructure.database.connection import get_db_session

# ========== Auth Use Cases ==========


@inject
def get_google_login_use_case(
    use_case_factory: Callable[..., GoogleLoginUseCase] = Provide[
        "identity.google_login_use_case_factory"
    ],
) -> GoogleLoginUseCase:
    """Get GoogleLoginUseCase instance.

    This use case doesn't need database session as it only redirects to Google OAuth.
    """
    return use_case_factory()


@inject
def get_google_callback_use_case(
    session: AsyncSession = Depends(get_db_session),
    user_repo_factory: Callable[[AsyncSession], IUserRepository] = Provide[
        "identity.user_repository"
    ],
    profile_repo_factory: Callable[[AsyncSession], IProfileRepository] = Provide[
        "identity.profile_repository"
    ],
    refresh_token_repo_factory: Callable[
        [AsyncSession], RefreshTokenRepository
    ] = Provide["identity.refresh_token_repository"],
    use_case_factory: Callable[..., GoogleCallbackUseCase] = Provide[
        "identity.google_callback_use_case_factory"
    ],
) -> GoogleCallbackUseCase:
    """Get GoogleCallbackUseCase instance with request-scope dependencies."""
    user_repo = user_repo_factory(session)
    profile_repo = profile_repo_factory(session)
    refresh_token_repo = refresh_token_repo_factory(session)
    return use_case_factory(
        user_repo=user_repo,
        profile_repo=profile_repo,
        refresh_token_repo=refresh_token_repo,
    )


@inject
def get_refresh_token_use_case(
    session: AsyncSession = Depends(get_db_session),
    user_repo_factory: Callable[[AsyncSession], IUserRepository] = Provide[
        "identity.user_repository"
    ],
    refresh_token_repo_factory: Callable[
        [AsyncSession], RefreshTokenRepository
    ] = Provide["identity.refresh_token_repository"],
    use_case_factory: Callable[..., RefreshTokenUseCase] = Provide[
        "identity.refresh_token_use_case_factory"
    ],
) -> RefreshTokenUseCase:
    """Get RefreshTokenUseCase instance with request-scope dependencies."""
    user_repo = user_repo_factory(session)
    refresh_token_repo = refresh_token_repo_factory(session)
    return use_case_factory(
        user_repo=user_repo, refresh_token_repo=refresh_token_repo
    )


@inject
def get_admin_login_use_case(
    session: AsyncSession = Depends(get_db_session),
    user_repo_factory: Callable[[AsyncSession], IUserRepository] = Provide[
        "identity.user_repository"
    ],
    refresh_token_repo_factory: Callable[
        [AsyncSession], RefreshTokenRepository
    ] = Provide["identity.refresh_token_repository"],
    use_case_factory: Callable[..., AdminLoginUseCase] = Provide[
        "identity.admin_login_use_case_factory"
    ],
) -> AdminLoginUseCase:
    """Get AdminLoginUseCase instance with request-scope dependencies."""
    user_repo = user_repo_factory(session)
    refresh_token_repo = refresh_token_repo_factory(session)
    return use_case_factory(
        user_repo=user_repo, refresh_token_repo=refresh_token_repo
    )


@inject
def get_logout_use_case(
    session: AsyncSession = Depends(get_db_session),
    refresh_token_repo_factory: Callable[
        [AsyncSession], RefreshTokenRepository
    ] = Provide["identity.refresh_token_repository"],
    use_case_factory: Callable[..., LogoutUseCase] = Provide[
        "identity.logout_use_case_factory"
    ],
) -> LogoutUseCase:
    """Get LogoutUseCase instance with request-scope dependencies."""
    refresh_token_repo = refresh_token_repo_factory(session)
    return use_case_factory(refresh_token_repo=refresh_token_repo)


# ========== Profile Use Cases ==========


@inject
def get_profile_use_case(
    session: AsyncSession = Depends(get_db_session),
    profile_repo_factory: Callable[[AsyncSession], IProfileRepository] = Provide[
        "identity.profile_repository"
    ],
    use_case_factory: Callable[..., GetProfileUseCase] = Provide[
        "identity.get_profile_use_case_factory"
    ],
) -> GetProfileUseCase:
    """Get GetProfileUseCase instance with request-scope dependencies."""
    profile_repo = profile_repo_factory(session)
    return use_case_factory(profile_repository=profile_repo)


@inject
def get_update_profile_use_case(
    session: AsyncSession = Depends(get_db_session),
    profile_repo_factory: Callable[[AsyncSession], IProfileRepository] = Provide[
        "identity.profile_repository"
    ],
    use_case_factory: Callable[..., UpdateProfileUseCase] = Provide[
        "identity.update_profile_use_case_factory"
    ],
) -> UpdateProfileUseCase:
    """Get UpdateProfileUseCase instance with request-scope dependencies."""
    profile_repo = profile_repo_factory(session)
    return use_case_factory(profile_repository=profile_repo)


# ========== Subscription Use Cases ==========


@inject
def get_verify_receipt_use_case(
    session: AsyncSession = Depends(get_db_session),
    subscription_repo_factory: Callable[
        [AsyncSession], SubscriptionRepository
    ] = Provide["identity.subscription_repository"],
    purchase_token_repo_factory: Callable[
        [AsyncSession], PurchaseTokenRepository
    ] = Provide["identity.purchase_token_repository"],
    use_case_factory: Callable[..., VerifyReceiptUseCase] = Provide[
        "identity.verify_receipt_use_case_factory"
    ],
) -> VerifyReceiptUseCase:
    """Get VerifyReceiptUseCase instance with request-scope dependencies."""
    subscription_repo = subscription_repo_factory(session)
    purchase_token_repo = purchase_token_repo_factory(session)
    return use_case_factory(
        subscription_repository=subscription_repo,
        purchase_token_repository=purchase_token_repo,
    )


@inject
def get_check_subscription_status_use_case(
    session: AsyncSession = Depends(get_db_session),
    subscription_repo_factory: Callable[
        [AsyncSession], SubscriptionRepository
    ] = Provide["identity.subscription_repository"],
    use_case_factory: Callable[..., CheckSubscriptionStatusUseCase] = Provide[
        "identity.check_subscription_status_use_case_factory"
    ],
) -> CheckSubscriptionStatusUseCase:
    """Get CheckSubscriptionStatusUseCase instance with request-scope dependencies."""
    subscription_repo = subscription_repo_factory(session)
    return use_case_factory(subscription_repository=subscription_repo)


@inject
def get_expire_subscriptions_use_case(
    session: AsyncSession = Depends(get_db_session),
    subscription_repo_factory: Callable[
        [AsyncSession], SubscriptionRepository
    ] = Provide["identity.subscription_repository"],
    use_case_factory: Callable[..., ExpireSubscriptionsUseCase] = Provide[
        "identity.expire_subscriptions_use_case_factory"
    ],
) -> ExpireSubscriptionsUseCase:
    """Get ExpireSubscriptionsUseCase instance with request-scope dependencies."""
    subscription_repo = subscription_repo_factory(session)
    return use_case_factory(subscription_repository=subscription_repo)
