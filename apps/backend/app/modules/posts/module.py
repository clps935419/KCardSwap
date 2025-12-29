"""Posts Module for dependency injection.

Provides city board posts related use cases using python-injector.
"""

from injector import Module, provider
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.infrastructure.repositories.subscription_repository_impl import (
    SubscriptionRepositoryImpl,
)
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
from app.modules.posts.application.use_cases.reject_interest_use_case import (
    RejectInterestUseCase,
)
from app.modules.posts.infrastructure.repositories.post_interest_repository_impl import (
    PostInterestRepositoryImpl,
)
from app.modules.posts.infrastructure.repositories.post_repository_impl import (
    PostRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)


class PostsModule(Module):
    """Posts module for python-injector.

    Provides city board posts related dependencies.
    """

    @provider
    def provide_create_post_use_case(self, session: AsyncSession) -> CreatePostUseCase:
        """Provide CreatePostUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        subscription_repo = SubscriptionRepositoryImpl(session)
        return CreatePostUseCase(
            post_repository=post_repo, subscription_repository=subscription_repo
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
        self, session: AsyncSession
    ) -> AcceptInterestUseCase:
        """Provide AcceptInterestUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        post_interest_repo = PostInterestRepositoryImpl(session)
        friendship_repo = FriendshipRepositoryImpl(session)
        chat_room_repo = ChatRoomRepositoryImpl(session)
        return AcceptInterestUseCase(
            post_repository=post_repo,
            post_interest_repository=post_interest_repo,
            friendship_repository=friendship_repo,
            chat_room_repository=chat_room_repo,
        )

    @provider
    def provide_reject_interest_use_case(
        self, session: AsyncSession
    ) -> RejectInterestUseCase:
        """Provide RejectInterestUseCase with dependencies."""
        post_interest_repo = PostInterestRepositoryImpl(session)
        return RejectInterestUseCase(post_interest_repository=post_interest_repo)

    @provider
    def provide_close_post_use_case(self, session: AsyncSession) -> ClosePostUseCase:
        """Provide ClosePostUseCase with dependencies."""
        post_repo = PostRepositoryImpl(session)
        return ClosePostUseCase(post_repository=post_repo)
