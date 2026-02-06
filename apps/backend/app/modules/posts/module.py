"""Posts Module for dependency injection.

Provides city board posts related use cases using python-injector.
"""

from injector import Module, provider
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
from app.modules.posts.application.use_cases.list_posts_v2_use_case import (
    ListPostsV2UseCase,
)
from app.modules.posts.application.use_cases.reject_interest_use_case import (
    RejectInterestUseCase,
)
from app.modules.posts.application.use_cases.toggle_like import ToggleLikeUseCase
from app.modules.posts.application.use_cases.get_post_use_case import GetPostUseCase
from app.modules.posts.infrastructure.repositories.post_interest_repository_impl import (
    PostInterestRepositoryImpl,
)
from app.modules.posts.infrastructure.repositories.post_like_repository_impl import (
    PostLikeRepositoryImpl,
)
from app.modules.posts.infrastructure.repositories.post_repository_impl import (
    PostRepositoryImpl,
)
from app.shared.domain.contracts.i_chat_room_service import IChatRoomService
from app.shared.domain.contracts.i_friendship_service import IFriendshipService
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)


class PostsModule(Module):
    """Posts module for python-injector.

    Provides city board posts related dependencies.
    """

    @provider
    def provide_create_post_use_case(
        self, session: AsyncSession, subscription_query_service: ISubscriptionQueryService
    ) -> CreatePostUseCase:
        """Provide CreatePostUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        return CreatePostUseCase(
            post_repository=post_repo, subscription_repository=subscription_query_service
        )

    @provider
    def provide_list_board_posts_use_case(
        self, session: AsyncSession
    ) -> ListBoardPostsUseCase:
        """Provide ListBoardPostsUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        return ListBoardPostsUseCase(post_repository=post_repo)

    @provider
    def provide_express_interest_use_case(
        self, session: AsyncSession
    ) -> ExpressInterestUseCase:
        """Provide ExpressInterestUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        post_interest_repo = PostInterestRepositoryImpl(session)
        return ExpressInterestUseCase(
            post_repository=post_repo, post_interest_repository=post_interest_repo
        )

    @provider
    def provide_accept_interest_use_case(
        self,
        session: AsyncSession,
        friendship_service: IFriendshipService,
        chat_room_service: IChatRoomService,
    ) -> AcceptInterestUseCase:
        """Provide AcceptInterestUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        post_interest_repo = PostInterestRepositoryImpl(session)
        return AcceptInterestUseCase(
            post_repository=post_repo,
            post_interest_repository=post_interest_repo,
            friendship_repository=friendship_service,
            chat_room_repository=chat_room_service,
        )

    @provider
    def provide_reject_interest_use_case(
        self, session: AsyncSession
    ) -> RejectInterestUseCase:
        """Provide RejectInterestUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        post_interest_repo = PostInterestRepositoryImpl(session)
        return RejectInterestUseCase(
            post_repository=post_repo,
            post_interest_repository=post_interest_repo
        )

    @provider
    def provide_close_post_use_case(self, session: AsyncSession) -> ClosePostUseCase:
        """Provide ClosePostUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        return ClosePostUseCase(post_repository=post_repo)

    @provider
    def provide_list_post_interests_use_case(
        self, session: AsyncSession
    ) -> ListPostInterestsUseCase:
        """Provide ListPostInterestsUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        post_interest_repo = PostInterestRepositoryImpl(session)
        return ListPostInterestsUseCase(
            post_repository=post_repo, post_interest_repository=post_interest_repo
        )

    @provider
    def provide_list_posts_v2_use_case(
        self, session: AsyncSession
    ) -> ListPostsV2UseCase:
        """Provide ListPostsV2UseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        like_repo = PostLikeRepositoryImpl(session)
        return ListPostsV2UseCase(
            post_repository=post_repo, like_repository=like_repo
        )

    @provider
    def provide_toggle_like_use_case(
        self, session: AsyncSession
    ) -> ToggleLikeUseCase:
        """Provide ToggleLikeUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        like_repo = PostLikeRepositoryImpl(session)
        return ToggleLikeUseCase(
            post_repository=post_repo, like_repository=like_repo
        )

    @provider
    def provide_get_post_use_case(
        self, session: AsyncSession
    ) -> GetPostUseCase:
        """Provide GetPostUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        return GetPostUseCase(post_repository=post_repo, session=session)
