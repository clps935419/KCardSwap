"""Posts Module Use Case Dependencies.

FastAPI dependency functions that connect request-scope dependencies
with IoC container providers to create use case instances.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    pass
from app.modules.identity.domain.repositories.i_subscription_repository import (
    ISubscriptionRepository,
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
from app.modules.posts.domain.repositories.i_post_interest_repository import (
    IPostInterestRepository,
)
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository
from app.modules.social.domain.repositories.i_chat_room_repository import (
    IChatRoomRepository,
)
from app.modules.social.domain.repositories.i_friendship_repository import (
    IFriendshipRepository,
)
from app.shared.infrastructure.database.connection import get_db_session

# ========== Posts Use Cases ==========


@inject
def get_create_post_use_case(
    session: AsyncSession = Depends(get_db_session),
    post_repo_factory: Callable[[AsyncSession], IPostRepository] = Depends(
        Provide["posts.post_repository"]
    ),
    subscription_repo_factory: Callable[
        [AsyncSession], ISubscriptionRepository
    ] = Depends(Provide["identity.subscription_repository"]),
    use_case_factory: Callable[..., CreatePostUseCase] = Depends(
        Provide["posts.create_post_use_case_factory"]
    ),
) -> CreatePostUseCase:
    """Get CreatePostUseCase instance with request-scope dependencies."""
    post_repo = post_repo_factory(session)
    subscription_repo = subscription_repo_factory(session)
    return use_case_factory(
        post_repository=post_repo, subscription_repository=subscription_repo
    )


@inject
def get_list_board_posts_use_case(
    session: AsyncSession = Depends(get_db_session),
    post_repo_factory: Callable[[AsyncSession], IPostRepository] = Depends(
        Provide["posts.post_repository"]
    ),
    use_case_factory: Callable[..., ListBoardPostsUseCase] = Depends(
        Provide["posts.list_board_posts_use_case_factory"]
    ),
) -> ListBoardPostsUseCase:
    """Get ListBoardPostsUseCase instance with request-scope dependencies."""
    post_repo = post_repo_factory(session)
    return use_case_factory(post_repository=post_repo)


@inject
def get_express_interest_use_case(
    session: AsyncSession = Depends(get_db_session),
    post_repo_factory: Callable[[AsyncSession], IPostRepository] = Depends(
        Provide["posts.post_repository"]
    ),
    post_interest_repo_factory: Callable[
        [AsyncSession], IPostInterestRepository
    ] = Depends(Provide["posts.post_interest_repository"]),
    use_case_factory: Callable[..., ExpressInterestUseCase] = Depends(
        Provide["posts.express_interest_use_case_factory"]
    ),
) -> ExpressInterestUseCase:
    """Get ExpressInterestUseCase instance with request-scope dependencies."""
    post_repo = post_repo_factory(session)
    post_interest_repo = post_interest_repo_factory(session)
    return use_case_factory(
        post_repository=post_repo, post_interest_repository=post_interest_repo
    )


@inject
def get_accept_interest_use_case(
    session: AsyncSession = Depends(get_db_session),
    post_repo_factory: Callable[[AsyncSession], IPostRepository] = Depends(
        Provide["posts.post_repository"]
    ),
    post_interest_repo_factory: Callable[
        [AsyncSession], IPostInterestRepository
    ] = Depends(Provide["posts.post_interest_repository"]),
    friendship_repo_factory: Callable[[AsyncSession], IFriendshipRepository] = Depends(
        Provide["social.friendship_repository"]
    ),
    chat_room_repo_factory: Callable[[AsyncSession], IChatRoomRepository] = Depends(
        Provide["social.chat_room_repository"]
    ),
    use_case_factory: Callable[..., AcceptInterestUseCase] = Depends(
        Provide["posts.accept_interest_use_case_factory"]
    ),
) -> AcceptInterestUseCase:
    """Get AcceptInterestUseCase instance with request-scope dependencies."""
    post_repo = post_repo_factory(session)
    post_interest_repo = post_interest_repo_factory(session)
    friendship_repo = friendship_repo_factory(session)
    chat_room_repo = chat_room_repo_factory(session)
    return use_case_factory(
        post_repository=post_repo,
        post_interest_repository=post_interest_repo,
        friendship_repository=friendship_repo,
        chat_room_repository=chat_room_repo,
    )


@inject
def get_reject_interest_use_case(
    session: AsyncSession = Depends(get_db_session),
    post_repo_factory: Callable[[AsyncSession], IPostRepository] = Depends(
        Provide["posts.post_repository"]
    ),
    post_interest_repo_factory: Callable[
        [AsyncSession], IPostInterestRepository
    ] = Depends(Provide["posts.post_interest_repository"]),
    use_case_factory: Callable[..., RejectInterestUseCase] = Depends(
        Provide["posts.reject_interest_use_case_factory"]
    ),
) -> RejectInterestUseCase:
    """Get RejectInterestUseCase instance with request-scope dependencies."""
    post_repo = post_repo_factory(session)
    post_interest_repo = post_interest_repo_factory(session)
    return use_case_factory(
        post_repository=post_repo, post_interest_repository=post_interest_repo
    )


@inject
def get_close_post_use_case(
    session: AsyncSession = Depends(get_db_session),
    post_repo_factory: Callable[[AsyncSession], IPostRepository] = Depends(
        Provide["posts.post_repository"]
    ),
    use_case_factory: Callable[..., ClosePostUseCase] = Depends(
        Provide["posts.close_post_use_case_factory"]
    ),
) -> ClosePostUseCase:
    """Get ClosePostUseCase instance with request-scope dependencies."""
    post_repo = post_repo_factory(session)
    return use_case_factory(post_repository=post_repo)
