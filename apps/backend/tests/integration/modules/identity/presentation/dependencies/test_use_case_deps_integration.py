"""
Integration tests for Identity Use Case Dependencies

Tests dependency injection with real app state and database sessions.
"""

import pytest
import pytest_asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from injector import Injector, Module, provider, singleton
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.modules.identity.domain.repositories.i_profile_repository import (
    IProfileRepository,
)
from app.modules.identity.domain.repositories.i_refresh_token_repository import (
    IRefreshTokenRepository,
)
from app.modules.identity.domain.repositories.i_subscription_repository import (
    ISubscriptionRepository,
)
from app.modules.identity.domain.repositories.i_user_repository import (
    IUserRepository,
)
from app.modules.identity.infrastructure.repositories.profile_repository_impl import (
    ProfileRepositoryImpl,
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
from app.modules.identity.infrastructure.external.google_oauth_service import (
    GoogleOAuthService,
)
from app.modules.identity.presentation.dependencies.use_case_deps import (
    get_get_profile_use_case,
    get_google_callback_use_case,
    get_google_login_use_case,
    get_logout_use_case,
    get_refresh_token_use_case,
    get_update_profile_use_case,
)
from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)
from app.shared.infrastructure.security.jwt_service import JWTService
from app.shared.infrastructure.security.password_hasher import PasswordHasher


class IdentityModule(Module):
    """Test module for identity dependencies"""

    @singleton
    @provider
    def provide_jwt_service(self) -> JWTService:
        return JWTService()

    @singleton
    @provider
    def provide_password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    @singleton
    @provider
    def provide_google_oauth_service(self) -> GoogleOAuthService:
        return GoogleOAuthService()

    @singleton
    @provider
    def provide_gcs_service(self) -> MockGCSStorageService:
        return MockGCSStorageService(bucket_name="test")

    @provider
    def provide_user_repository(self, session: AsyncSession) -> IUserRepository:
        return UserRepositoryImpl(session)

    @provider
    def provide_profile_repository(self, session: AsyncSession) -> IProfileRepository:
        return ProfileRepositoryImpl(session)

    @provider
    def provide_refresh_token_repository(
        self, session: AsyncSession
    ) -> IRefreshTokenRepository:
        return RefreshTokenRepositoryImpl(session)

    @provider
    def provide_subscription_repository(
        self, session: AsyncSession
    ) -> ISubscriptionRepository:
        return SubscriptionRepositoryImpl(session)

    @provider
    def provide_google_login_use_case(
        self,
        session: AsyncSession,
        google_oauth_service: GoogleOAuthService,
        jwt_service: JWTService,
    ) -> GoogleLoginUseCase:
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
        self,
        session: AsyncSession,
        jwt_service: JWTService,
    ) -> RefreshTokenUseCase:
        refresh_token_repo = RefreshTokenRepositoryImpl(session)
        return RefreshTokenUseCase(
            refresh_token_repo=refresh_token_repo,
            jwt_service=jwt_service,
        )

    @provider
    def provide_logout_use_case(
        self,
        session: AsyncSession,
    ) -> LogoutUseCase:
        refresh_token_repo = RefreshTokenRepositoryImpl(session)
        return LogoutUseCase(refresh_token_repo=refresh_token_repo)

    @provider
    def provide_get_profile_use_case(
        self,
        session: AsyncSession,
    ) -> GetProfileUseCase:
        profile_repo = ProfileRepositoryImpl(session)
        return GetProfileUseCase(profile_repo=profile_repo)

    @provider
    def provide_update_profile_use_case(
        self,
        session: AsyncSession,
    ) -> UpdateProfileUseCase:
        profile_repo = ProfileRepositoryImpl(session)
        return UpdateProfileUseCase(profile_repo=profile_repo)


class TestIdentityUseCaseDependenciesIntegration:
    """Integration tests for Identity use case dependencies"""

    @pytest.fixture
    def test_injector(self):
        """Create test injector with identity module"""
        return Injector([IdentityModule()])

    @pytest.fixture
    def test_app_with_injector(self, test_injector):
        """Create test app with injector in state"""
        app = FastAPI()
        app.state.injector = test_injector
        return app

    @pytest.mark.asyncio
    async def test_get_google_login_use_case(
        self, test_app_with_injector, db_session
    ):
        """Test get_google_login_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_google_login_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, GoogleLoginUseCase)

    @pytest.mark.asyncio
    async def test_get_google_callback_use_case(
        self, test_app_with_injector, db_session
    ):
        """Test get_google_callback_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_google_callback_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, GoogleCallbackUseCase)

    @pytest.mark.asyncio
    async def test_get_refresh_token_use_case(
        self, test_app_with_injector, db_session
    ):
        """Test get_refresh_token_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_refresh_token_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, RefreshTokenUseCase)

    @pytest.mark.asyncio
    async def test_get_logout_use_case(self, test_app_with_injector, db_session):
        """Test get_logout_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_logout_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, LogoutUseCase)

    @pytest.mark.asyncio
    async def test_get_get_profile_use_case(
        self, test_app_with_injector, db_session
    ):
        """Test get_get_profile_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_get_profile_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, GetProfileUseCase)

    @pytest.mark.asyncio
    async def test_get_update_profile_use_case(
        self, test_app_with_injector, db_session
    ):
        """Test get_update_profile_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_update_profile_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, UpdateProfileUseCase)

    @pytest.mark.asyncio
    async def test_use_case_has_correct_dependencies(
        self, test_app_with_injector, db_session
    ):
        """Test that use case has correct repository dependencies"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_get_profile_use_case(db_session, mock_request)

        # Assert
        assert hasattr(use_case, "profile_repo")
        assert use_case.profile_repo is not None

    @pytest.mark.asyncio
    async def test_child_injector_isolation(
        self, test_app_with_injector, db_session
    ):
        """Test that each request gets isolated child injector"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request1 = MagicMock(spec=Request)
        mock_request1.app = test_app_with_injector
        mock_request2 = MagicMock(spec=Request)
        mock_request2.app = test_app_with_injector

        # Act
        use_case1 = await get_get_profile_use_case(db_session, mock_request1)
        use_case2 = await get_get_profile_use_case(db_session, mock_request2)

        # Assert
        assert use_case1 is not use_case2  # Different instances

    @pytest.mark.asyncio
    async def test_session_binding_in_child_injector(
        self, test_app_with_injector, db_session
    ):
        """Test that session is correctly bound in child injector"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_get_profile_use_case(db_session, mock_request)

        # Assert - Use case should have repository with correct session
        assert use_case.profile_repo._session is db_session
