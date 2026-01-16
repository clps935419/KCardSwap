"""Identity Module for dependency injection.

Provides identity and authentication related use cases using python-injector.
"""

from injector import Module, provider, singleton
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
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
from app.modules.identity.infrastructure.external.google_oauth_service import (
    GoogleOAuthService,
)
from app.modules.identity.infrastructure.external.google_play_billing_service import (
    GooglePlayBillingService,
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
from app.modules.identity.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.modules.identity.infrastructure.security.password_service import (
    PasswordService,
)
from app.modules.identity.application.services.profile_query_service_impl import (
    ProfileQueryServiceImpl,
)
from app.modules.identity.application.services.subscription_query_service_impl import (
    SubscriptionQueryServiceImpl,
)
from app.modules.identity.application.services.user_basic_info_service_impl import (
    UserBasicInfoServiceImpl,
)
from app.shared.domain.contracts.i_profile_query_service import IProfileQueryService
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)
from app.shared.domain.contracts.i_user_basic_info_service import IUserBasicInfoService
from app.shared.infrastructure.security.jwt_service import JWTService


class IdentityModule(Module):
    """Identity module for python-injector.

    Provides identity and authentication related dependencies.
    """

    @provider
    @singleton
    def provide_google_oauth_service(self) -> GoogleOAuthService:
        """Provide Google OAuth service."""
        return GoogleOAuthService()

    # Auth Use Cases
    @provider
    def provide_google_login_use_case(
        self,
        session: AsyncSession,
        google_oauth_service: GoogleOAuthService,
        jwt_service: JWTService,
    ) -> GoogleLoginUseCase:
        """Provide GoogleLoginUseCase with dependencies."""
        user_repo = UserRepositoryImpl(session)
        profile_repo = ProfileRepositoryImpl(session)
        refresh_token_repo = RefreshTokenRepositoryImpl(session)
        return GoogleLoginUseCase(
            user_repo=user_repo,
            profile_repo=profile_repo,
            refresh_token_repo=refresh_token_repo,
            google_oauth_service=google_oauth_service,
            jwt_service=jwt_service,
        )

    @provider
    def provide_google_callback_use_case(
        self,
        session: AsyncSession,
        google_oauth_service: GoogleOAuthService,
        jwt_service: JWTService,
    ) -> GoogleCallbackUseCase:
        """Provide GoogleCallbackUseCase with dependencies."""
        user_repo = UserRepositoryImpl(session)
        profile_repo = ProfileRepositoryImpl(session)
        refresh_token_repo = RefreshTokenRepositoryImpl(session)
        return GoogleCallbackUseCase(
            user_repo=user_repo,
            profile_repo=profile_repo,
            refresh_token_repo=refresh_token_repo,
            google_oauth_service=google_oauth_service,
            jwt_service=jwt_service,
        )

    @provider
    def provide_refresh_token_use_case(
        self, session: AsyncSession, jwt_service: JWTService
    ) -> RefreshTokenUseCase:
        """Provide RefreshTokenUseCase with dependencies."""
        refresh_token_repo = RefreshTokenRepositoryImpl(session)
        return RefreshTokenUseCase(
            refresh_token_repo=refresh_token_repo,
            jwt_service=jwt_service,
        )

    @provider
    def provide_logout_use_case(self, session: AsyncSession) -> LogoutUseCase:
        """Provide LogoutUseCase with dependencies."""
        refresh_token_repo = RefreshTokenRepositoryImpl(session)
        return LogoutUseCase(refresh_token_repo=refresh_token_repo)

    @provider
    def provide_admin_login_use_case(
        self, session: AsyncSession, jwt_service: JWTService
    ) -> AdminLoginUseCase:
        """Provide AdminLoginUseCase with dependencies."""
        user_repo = UserRepositoryImpl(session)
        refresh_token_repo = RefreshTokenRepositoryImpl(session)
        password_service = PasswordService()
        return AdminLoginUseCase(
            user_repo=user_repo,
            refresh_token_repo=refresh_token_repo,
            password_service=password_service,
            jwt_service=jwt_service,
        )

    # Profile Use Cases
    @provider
    def provide_get_profile_use_case(self, session: AsyncSession) -> GetProfileUseCase:
        """Provide GetProfileUseCase with dependencies."""
        profile_repo = ProfileRepositoryImpl(session)
        return GetProfileUseCase(profile_repo=profile_repo)

    @provider
    def provide_update_profile_use_case(
        self, session: AsyncSession
    ) -> UpdateProfileUseCase:
        """Provide UpdateProfileUseCase with dependencies."""
        profile_repo = ProfileRepositoryImpl(session)
        return UpdateProfileUseCase(profile_repo=profile_repo)

    # Subscription Use Cases
    @provider
    def provide_verify_receipt_use_case(
        self, session: AsyncSession, settings: Settings
    ) -> VerifyReceiptUseCase:
        """Provide VerifyReceiptUseCase with dependencies.
        
        Note: Billing service initialization is optional. If credentials are not
        provided, the service will raise an error only when actually used, not
        during module initialization. This allows tests to mock the service.
        """
        subscription_repo = SubscriptionRepositoryImpl(session)
        purchase_token_repo = PurchaseTokenRepositoryImpl(session)
        
        # Initialize billing service with optional credentials
        # This allows tests to mock without needing real credentials
        try:
            billing_service = GooglePlayBillingService(
                package_name=settings.GOOGLE_PLAY_PACKAGE_NAME or "test.package",
                service_account_key_path=settings.GOOGLE_PLAY_SERVICE_ACCOUNT_KEY_PATH,
            )
        except ValueError:
            # If no credentials provided, create a placeholder that will be mocked in tests
            # In production, this will fail at use-time, not initialization-time
            billing_service = None  # type: ignore
        
        return VerifyReceiptUseCase(
            subscription_repository=subscription_repo,
            purchase_token_repository=purchase_token_repo,
            billing_service=billing_service,  # type: ignore
        )

    @provider
    def provide_check_subscription_status_use_case(
        self, session: AsyncSession
    ) -> CheckSubscriptionStatusUseCase:
        """Provide CheckSubscriptionStatusUseCase with dependencies."""
        subscription_repo = SubscriptionRepositoryImpl(session)
        return CheckSubscriptionStatusUseCase(subscription_repository=subscription_repo)

    @provider
    def provide_expire_subscriptions_use_case(
        self, session: AsyncSession
    ) -> ExpireSubscriptionsUseCase:
        """Provide ExpireSubscriptionsUseCase with dependencies."""
        subscription_repo = SubscriptionRepositoryImpl(session)
        return ExpireSubscriptionsUseCase(subscription_repository=subscription_repo)

    # Shared Contract Services - For cross-bounded-context communication
    @provider
    def provide_subscription_query_service(
        self, session: AsyncSession
    ) -> ISubscriptionQueryService:
        """Provide ISubscriptionQueryService implementation."""
        subscription_repo = SubscriptionRepositoryImpl(session)
        return SubscriptionQueryServiceImpl(subscription_repository=subscription_repo)

    @provider
    def provide_profile_query_service(
        self, session: AsyncSession
    ) -> IProfileQueryService:
        """Provide IProfileQueryService implementation."""
        profile_repo = ProfileRepositoryImpl(session)
        return ProfileQueryServiceImpl(profile_repository=profile_repo)

    @provider
    def provide_user_basic_info_service(
        self, session: AsyncSession
    ) -> IUserBasicInfoService:
        """Provide IUserBasicInfoService implementation."""
        profile_repo = ProfileRepositoryImpl(session)
        return UserBasicInfoServiceImpl(profile_repository=profile_repo)
