"""
Integration tests for Posts Use Case Dependencies

Tests dependency injection for Posts module with real app state.
"""

import pytest
from fastapi import FastAPI, Request
from injector import Injector, Module, provider, singleton
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.application.use_cases.create_post_use_case import (
    CreatePostUseCase,
)
from app.modules.posts.application.use_cases.list_board_posts_use_case import (
    ListBoardPostsUseCase,
)
from app.modules.posts.application.use_cases.toggle_like import ToggleLikeUseCase
from app.modules.posts.domain.repositories.i_post_interest_repository import (
    IPostInterestRepository,
)
from app.modules.posts.domain.repositories.i_post_like_repository import (
    IPostLikeRepository,
)
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository
from app.modules.posts.infrastructure.repositories.post_interest_repository_impl import (
    PostInterestRepositoryImpl,
)
from app.modules.posts.infrastructure.repositories.post_like_repository_impl import (
    PostLikeRepositoryImpl,
)
from app.modules.posts.infrastructure.repositories.post_repository_impl import (
    PostRepositoryImpl,
)
from app.modules.posts.presentation.dependencies.use_case_deps import (
    get_create_post_use_case,
    get_list_board_posts_use_case,
    get_toggle_like_use_case,
)
from app.modules.identity.application.services.subscription_query_service_impl import (
    SubscriptionQueryServiceImpl,
)
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import (
    SubscriptionRepositoryImpl,
)
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)
from app.shared.infrastructure.external.mock_gcs_storage_service import (
    MockGCSStorageService,
)


class PostsModule(Module):
    """Test module for posts dependencies"""

    @singleton
    @provider
    def provide_gcs_service(self) -> MockGCSStorageService:
        return MockGCSStorageService(bucket_name="test")

    @provider
    def provide_post_repository(self, session: AsyncSession) -> IPostRepository:
        return PostRepositoryImpl(session)

    @provider
    def provide_interest_repository(
        self, session: AsyncSession
    ) -> IPostInterestRepository:
        return PostInterestRepositoryImpl(session)

    @provider
    def provide_like_repository(self, session: AsyncSession) -> IPostLikeRepository:
        return PostLikeRepositoryImpl(session)

    @provider
    def provide_subscription_query_service(
        self, session: AsyncSession
    ) -> ISubscriptionQueryService:
        subscription_repo = SubscriptionRepositoryImpl(session)
        return SubscriptionQueryServiceImpl(subscription_repository=subscription_repo)

    @provider
    def provide_create_post_use_case(
        self,
        post_repository: IPostRepository,
        subscription_repository: ISubscriptionQueryService,
    ) -> CreatePostUseCase:
        return CreatePostUseCase(
            post_repository=post_repository,
            subscription_repository=subscription_repository,
        )

    @provider
    def provide_list_board_posts_use_case(
        self,
        post_repository: IPostRepository,
    ) -> ListBoardPostsUseCase:
        return ListBoardPostsUseCase(post_repository=post_repository)

    @provider
    def provide_toggle_like_use_case(
        self,
        post_repository: IPostRepository,
        like_repository: IPostLikeRepository,
    ) -> ToggleLikeUseCase:
        return ToggleLikeUseCase(
            post_repository=post_repository,
            like_repository=like_repository,
        )


class TestPostsUseCaseDependenciesIntegration:
    """Integration tests for Posts use case dependencies"""

    @pytest.fixture
    def test_injector(self):
        """Create test injector with posts module"""
        return Injector([PostsModule()])

    @pytest.fixture
    def test_app_with_injector(self, test_injector):
        """Create test app with injector in state"""
        app = FastAPI()
        app.state.injector = test_injector
        return app

    @pytest.mark.asyncio
    async def test_get_create_post_use_case(
        self, test_app_with_injector, db_session
    ):
        """Test get_create_post_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_create_post_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, CreatePostUseCase)

    @pytest.mark.asyncio
    async def test_get_list_board_posts_use_case(
        self, test_app_with_injector, db_session
    ):
        """Test get_list_board_posts_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_list_board_posts_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, ListBoardPostsUseCase)

    @pytest.mark.asyncio
    async def test_get_toggle_like_use_case(
        self, test_app_with_injector, db_session
    ):
        """Test get_toggle_like_use_case dependency"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_toggle_like_use_case(db_session, mock_request)

        # Assert
        assert use_case is not None
        assert isinstance(use_case, ToggleLikeUseCase)

    @pytest.mark.asyncio
    async def test_use_case_has_correct_repositories(
        self, test_app_with_injector, db_session
    ):
        """Test that use case has correct repository dependencies"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_create_post_use_case(db_session, mock_request)

        # Assert
        assert hasattr(use_case, "post_repository")
        assert use_case.post_repository is not None

    @pytest.mark.asyncio
    async def test_session_correctly_bound(
        self, test_app_with_injector, db_session
    ):
        """Test that session is correctly bound in child injector"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.app = test_app_with_injector

        # Act
        use_case = await get_create_post_use_case(db_session, mock_request)

        # Assert
        assert use_case.post_repository._session is db_session

    @pytest.mark.asyncio
    async def test_multiple_use_cases_isolated(
        self, test_app_with_injector, db_session
    ):
        """Test that multiple use cases get isolated child injectors"""
        # Arrange
        from unittest.mock import MagicMock

        mock_request1 = MagicMock(spec=Request)
        mock_request1.app = test_app_with_injector
        mock_request2 = MagicMock(spec=Request)
        mock_request2.app = test_app_with_injector

        # Act
        use_case1 = await get_create_post_use_case(db_session, mock_request1)
        use_case2 = await get_create_post_use_case(db_session, mock_request2)

        # Assert
        assert use_case1 is not use_case2  # Different instances
