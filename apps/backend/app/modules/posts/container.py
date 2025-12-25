"""Posts Module Container.

IoC container for managing Posts module dependencies.
Declares providers for repositories and use cases.
"""

from dependency_injector import containers, providers

# Import repositories
from app.modules.posts.infrastructure.repositories.post_repository_impl import (
    PostRepositoryImpl,
)
from app.modules.posts.infrastructure.repositories.post_interest_repository_impl import (
    PostInterestRepositoryImpl,
)

# Import use cases
from app.modules.posts.application.use_cases.create_post_use_case import (
    CreatePostUseCase,
)
from app.modules.posts.application.use_cases.list_board_posts_use_case import (
    ListBoardPostsUseCase,
)
from app.modules.posts.application.use_cases.express_interest_use_case import (
    ExpressInterestUseCase,
)
from app.modules.posts.application.use_cases.accept_interest_use_case import (
    AcceptInterestUseCase,
)
from app.modules.posts.application.use_cases.reject_interest_use_case import (
    RejectInterestUseCase,
)
from app.modules.posts.application.use_cases.close_post_use_case import (
    ClosePostUseCase,
)


class PostsModuleContainer(containers.DeclarativeContainer):
    """Posts module container.

    Provides city board posts related dependencies including:
    - Repositories (post, post_interest)
    - Use cases (create, list, express interest, accept/reject interest, close)
    """

    # Shared dependencies from parent container
    shared = providers.DependenciesContainer()

    # ========== Repositories ==========
    # All repositories need request-scope session: use Factory, session passed by caller
    post_repository = providers.Factory(PostRepositoryImpl)
    post_interest_repository = providers.Factory(PostInterestRepositoryImpl)

    # ========== Use Case Factories ==========
    create_post_use_case_factory = providers.Factory(CreatePostUseCase)

    list_board_posts_use_case_factory = providers.Factory(ListBoardPostsUseCase)

    express_interest_use_case_factory = providers.Factory(ExpressInterestUseCase)

    accept_interest_use_case_factory = providers.Factory(AcceptInterestUseCase)

    reject_interest_use_case_factory = providers.Factory(RejectInterestUseCase)

    close_post_use_case_factory = providers.Factory(ClosePostUseCase)
