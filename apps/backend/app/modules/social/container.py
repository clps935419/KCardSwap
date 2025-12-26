"""Social Module Container.

IoC container for managing Social module dependencies.
Declares providers for repositories, services, and use cases.
"""

from dependency_injector import containers, providers

from app.modules.social.application.use_cases.cards.check_quota import (
    CheckUploadQuotaUseCase,
)
from app.modules.social.application.use_cases.cards.delete_card import DeleteCardUseCase
from app.modules.social.application.use_cases.cards.get_my_cards import (
    GetMyCardsUseCase,
)

# Import use cases - Cards
from app.modules.social.application.use_cases.cards.upload_card import UploadCardUseCase
from app.modules.social.application.use_cases.chat.get_messages_use_case import (
    GetMessagesUseCase,
)

# Import use cases - Chat
from app.modules.social.application.use_cases.chat.send_message_use_case import (
    SendMessageUseCase,
)
from app.modules.social.application.use_cases.friends.accept_friend_request_use_case import (
    AcceptFriendRequestUseCase,
)
from app.modules.social.application.use_cases.friends.block_user_use_case import (
    BlockUserUseCase,
)

# Import use cases - Friends
from app.modules.social.application.use_cases.friends.send_friend_request_use_case import (
    SendFriendRequestUseCase,
)

# Import use cases - Nearby
from app.modules.social.application.use_cases.nearby.search_nearby_cards_use_case import (
    SearchNearbyCardsUseCase,
)
from app.modules.social.application.use_cases.nearby.update_user_location_use_case import (
    UpdateUserLocationUseCase,
)

# Import use cases - Ratings
from app.modules.social.application.use_cases.ratings.rate_user_use_case import (
    RateUserUseCase,
)

# Import use cases - Reports
from app.modules.social.application.use_cases.reports.report_user_use_case import (
    ReportUserUseCase,
)
from app.modules.social.application.use_cases.trades.accept_trade_use_case import (
    AcceptTradeUseCase,
)
from app.modules.social.application.use_cases.trades.cancel_trade_use_case import (
    CancelTradeUseCase,
)
from app.modules.social.application.use_cases.trades.complete_trade_use_case import (
    CompleteTradeUseCase,
)

# Import use cases - Trades
from app.modules.social.application.use_cases.trades.create_trade_proposal_use_case import (
    CreateTradeProposalUseCase,
)
from app.modules.social.application.use_cases.trades.get_trade_history_use_case import (
    GetTradeHistoryUseCase,
)
from app.modules.social.application.use_cases.trades.reject_trade_use_case import (
    RejectTradeUseCase,
)

# Import domain services
from app.modules.social.domain.services.card_validation_service import (
    CardValidationService,
)
from app.modules.social.domain.services.trade_validation_service import (
    TradeValidationService,
)

# Import repositories (alphabetical)
from app.modules.social.infrastructure.repositories.card_repository_impl import (
    CardRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.message_repository_impl import (
    MessageRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.rating_repository_impl import (
    RatingRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.report_repository_impl import (
    ReportRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.trade_repository_impl import (
    TradeRepositoryImpl,
)

# Import infrastructure services
from app.modules.social.infrastructure.services.search_quota_service import (
    SearchQuotaService,
)


class SocialModuleContainer(containers.DeclarativeContainer):
    """Social module container.

    Provides social features related dependencies including:
    - Repositories (card, friendship, chat, rating, report, trade)
    - Domain services (validation services)
    - Use cases (cards, nearby, friends, chat, ratings, reports, trades)
    """

    # Shared dependencies from parent container
    shared = providers.DependenciesContainer()

    # ========== Repositories ==========
    # All repositories need request-scope session: use Factory, session passed by caller
    card_repository = providers.Factory(CardRepositoryImpl)
    friendship_repository = providers.Factory(FriendshipRepositoryImpl)
    chat_room_repository = providers.Factory(ChatRoomRepositoryImpl)
    message_repository = providers.Factory(MessageRepositoryImpl)
    rating_repository = providers.Factory(RatingRepositoryImpl)
    report_repository = providers.Factory(ReportRepositoryImpl)
    trade_repository = providers.Factory(TradeRepositoryImpl)

    # ========== Domain Services ==========
    card_validation_service = providers.Factory(CardValidationService)
    trade_validation_service = providers.Factory(TradeValidationService)

    # ========== Infrastructure Services ==========
    search_quota_service = providers.Factory(SearchQuotaService)

    # ========== Use Case Factories - Cards ==========
    upload_card_use_case_factory = providers.Factory(
        UploadCardUseCase,
        validation_service=card_validation_service,
        gcs_service=shared.gcs_storage_provider,
    )

    get_my_cards_use_case_factory = providers.Factory(GetMyCardsUseCase)

    delete_card_use_case_factory = providers.Factory(
        DeleteCardUseCase,
        gcs_service=shared.gcs_storage_provider,
    )

    check_quota_use_case_factory = providers.Factory(CheckUploadQuotaUseCase)

    # ========== Use Case Factories - Nearby ==========
    search_nearby_cards_use_case_factory = providers.Factory(
        SearchNearbyCardsUseCase,
        quota_service=search_quota_service,
    )

    update_user_location_use_case_factory = providers.Factory(UpdateUserLocationUseCase)

    # ========== Use Case Factories - Friends ==========
    send_friend_request_use_case_factory = providers.Factory(SendFriendRequestUseCase)

    accept_friend_request_use_case_factory = providers.Factory(
        AcceptFriendRequestUseCase
    )

    block_user_use_case_factory = providers.Factory(BlockUserUseCase)

    # ========== Use Case Factories - Chat ==========
    send_message_use_case_factory = providers.Factory(SendMessageUseCase)

    get_messages_use_case_factory = providers.Factory(GetMessagesUseCase)

    # ========== Use Case Factories - Ratings ==========
    rate_user_use_case_factory = providers.Factory(RateUserUseCase)

    # ========== Use Case Factories - Reports ==========
    report_user_use_case_factory = providers.Factory(ReportUserUseCase)

    # ========== Use Case Factories - Trades ==========
    create_trade_proposal_use_case_factory = providers.Factory(
        CreateTradeProposalUseCase,
        validation_service=trade_validation_service,
    )

    accept_trade_use_case_factory = providers.Factory(
        AcceptTradeUseCase,
        validation_service=trade_validation_service,
    )

    cancel_trade_use_case_factory = providers.Factory(CancelTradeUseCase)

    reject_trade_use_case_factory = providers.Factory(RejectTradeUseCase)

    complete_trade_use_case_factory = providers.Factory(CompleteTradeUseCase)

    get_trade_history_use_case_factory = providers.Factory(GetTradeHistoryUseCase)
