"""Identity Module Container.

IoC container for managing Identity module dependencies.
Declares providers for repositories, services, and use cases.
"""

from dependency_injector import containers, providers

from app.modules.identity.application.use_cases.auth.admin_login import (
    AdminLoginUseCase,
)
from app.modules.identity.application.use_cases.auth.google_callback import (
    GoogleCallbackUseCase,
)

# Import use cases - Auth
from app.modules.identity.application.use_cases.auth.login_with_google import (
    GoogleLoginUseCase,
)
from app.modules.identity.application.use_cases.auth.logout import LogoutUseCase
from app.modules.identity.application.use_cases.auth.refresh_token import (
    RefreshTokenUseCase,
)

# Import use cases - Profile
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

# Import use cases - Subscription
from app.modules.identity.application.use_cases.subscription.verify_receipt_use_case import (
    VerifyReceiptUseCase,
)

# Import external services
from app.modules.identity.infrastructure.external.google_oauth_service import (
    GoogleOAuthService,
)
from app.modules.identity.infrastructure.repositories.profile_repository_impl import (
    ProfileRepositoryImpl,
)
from app.modules.identity.infrastructure.repositories.purchase_token_repository_impl import (
    PurchaseTokenRepositoryImpl,
)
from app.modules.identity.infrastructure.repositories.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import (
    SubscriptionRepositoryImpl,
)

# Import repositories
from app.modules.identity.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)

# Import security services
from app.modules.identity.infrastructure.security.password_service import (
    PasswordService,
)


class IdentityModuleContainer(containers.DeclarativeContainer):
    """Identity module container.

    Provides identity and authentication related dependencies including:
    - Repositories (user, profile, refresh_token, subscription, purchase_token)
    - External services (Google OAuth)
    - Security services (password service)
    - Use cases (auth, profile, subscription)
    """

    # Shared dependencies from parent container
    shared = providers.DependenciesContainer()

    # ========== Repositories ==========
    # All repositories need request-scope session: use Factory, session passed by caller
    user_repository = providers.Factory(UserRepositoryImpl)
    profile_repository = providers.Factory(ProfileRepositoryImpl)
    refresh_token_repository = providers.Factory(RefreshTokenRepositoryImpl)
    subscription_repository = providers.Factory(SubscriptionRepositoryImpl)
    purchase_token_repository = providers.Factory(PurchaseTokenRepositoryImpl)

    # ========== External Services ==========
    google_oauth_service = providers.Singleton(GoogleOAuthService)

    # ========== Security Services ==========
    password_service = providers.Singleton(PasswordService)

    # ========== Use Case Factories - Auth ==========
    google_login_use_case_factory = providers.Factory(
        GoogleLoginUseCase,
        google_oauth_service=google_oauth_service,
        jwt_service=shared.jwt_service_provider,
    )

    google_callback_use_case_factory = providers.Factory(
        GoogleCallbackUseCase,
        google_oauth_service=google_oauth_service,
        jwt_service=shared.jwt_service_provider,
    )

    refresh_token_use_case_factory = providers.Factory(
        RefreshTokenUseCase,
        jwt_service=shared.jwt_service_provider,
    )

    admin_login_use_case_factory = providers.Factory(
        AdminLoginUseCase,
        password_service=password_service,
        jwt_service=shared.jwt_service_provider,
    )

    logout_use_case_factory = providers.Factory(LogoutUseCase)

    # ========== Use Case Factories - Profile ==========
    get_profile_use_case_factory = providers.Factory(GetProfileUseCase)

    update_profile_use_case_factory = providers.Factory(UpdateProfileUseCase)

    # ========== Use Case Factories - Subscription ==========
    verify_receipt_use_case_factory = providers.Factory(VerifyReceiptUseCase)

    check_subscription_status_use_case_factory = providers.Factory(
        CheckSubscriptionStatusUseCase
    )

    expire_subscriptions_use_case_factory = providers.Factory(
        ExpireSubscriptionsUseCase
    )
