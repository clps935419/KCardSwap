"""Social Module for dependency injection.

Provides social features related use cases using python-injector.
"""

from injector import Module, provider
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.application.services.chat_room_service_impl import (
    ChatRoomServiceImpl,
)
from app.modules.social.application.services.friendship_service_impl import (
    FriendshipServiceImpl,
)
from app.modules.social.application.use_cases.cards.check_quota import (
    CheckUploadQuotaUseCase,
)
from app.modules.social.application.use_cases.cards.delete_card import (
    DeleteCardUseCase,
)
from app.modules.social.application.use_cases.cards.get_my_cards import (
    GetMyCardsUseCase,
)
from app.modules.social.application.use_cases.cards.upload_card import (
    UploadCardUseCase,
)
from app.modules.social.application.use_cases.chat.get_messages_use_case import (
    GetMessagesUseCase,
)
from app.modules.social.application.use_cases.chat.send_message_use_case import (
    SendMessageUseCase,
)
from app.modules.social.application.use_cases.friends.accept_friend_request_use_case import (
    AcceptFriendRequestUseCase,
)
from app.modules.social.application.use_cases.friends.block_user_use_case import (
    BlockUserUseCase,
)
from app.modules.social.application.use_cases.friends.send_friend_request_use_case import (
    SendFriendRequestUseCase,
)
from app.modules.social.application.use_cases.nearby.search_nearby_cards_use_case import (
    SearchNearbyCardsUseCase,
)
from app.modules.social.application.use_cases.nearby.update_user_location_use_case import (
    UpdateUserLocationUseCase,
)
from app.modules.social.application.use_cases.ratings.rate_user_use_case import (
    RateUserUseCase,
)
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
from app.modules.social.application.use_cases.trades.create_trade_proposal_use_case import (
    CreateTradeProposalUseCase,
)
from app.modules.social.application.use_cases.trades.get_trade_history_use_case import (
    GetTradeHistoryUseCase,
)
from app.modules.social.application.use_cases.trades.reject_trade_use_case import (
    RejectTradeUseCase,
)
from app.modules.social.domain.services.card_validation_service import (
    CardValidationService,
)
from app.modules.social.infrastructure.repositories.card_repository_impl import (
    CardRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
    ChatRoomRepositoryImpl,
)
from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
    FriendshipRepositoryImpl,
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
from app.shared.domain.contracts.i_chat_room_service import IChatRoomService
from app.shared.domain.contracts.i_friendship_service import IFriendshipService
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)
from app.shared.infrastructure.external.gcs_storage_service import GCSStorageService


class SocialModule(Module):
    """Social module for python-injector.

    Provides social features related dependencies.
    """

    # Card Use Cases
    @provider
    def provide_upload_card_use_case(
        self,
        session: AsyncSession,
        gcs_storage: GCSStorageService,
        subscription_query_service: ISubscriptionQueryService,
    ) -> UploadCardUseCase:
        """Provide UploadCardUseCase with dependencies."""
        card_repo = CardRepositoryImpl(session)
        card_validation_service = CardValidationService()
        return UploadCardUseCase(
            card_repository=card_repo,
            subscription_repository=subscription_query_service,
            storage_service=gcs_storage,
            validation_service=card_validation_service,
        )

    @provider
    def provide_get_my_cards_use_case(self, session: AsyncSession) -> GetMyCardsUseCase:
        """Provide GetMyCardsUseCase with dependencies."""
        card_repo = CardRepositoryImpl(session)
        return GetMyCardsUseCase(card_repository=card_repo)

    @provider
    def provide_delete_card_use_case(
        self, session: AsyncSession, gcs_storage: GCSStorageService
    ) -> DeleteCardUseCase:
        """Provide DeleteCardUseCase with dependencies."""
        card_repo = CardRepositoryImpl(session)
        return DeleteCardUseCase(card_repository=card_repo, storage_service=gcs_storage)

    @provider
    def provide_check_quota_use_case(
        self, session: AsyncSession, subscription_query_service: ISubscriptionQueryService
    ) -> CheckUploadQuotaUseCase:
        """Provide CheckUploadQuotaUseCase with dependencies."""
        card_repo = CardRepositoryImpl(session)
        return CheckUploadQuotaUseCase(
            card_repository=card_repo, subscription_repository=subscription_query_service
        )

    # Nearby Use Cases
    @provider
    def provide_search_nearby_cards_use_case(
        self, session: AsyncSession
    ) -> SearchNearbyCardsUseCase:
        """Provide SearchNearbyCardsUseCase with dependencies."""
        card_repo = CardRepositoryImpl(session)
        return SearchNearbyCardsUseCase(card_repository=card_repo)

    @provider
    def provide_update_user_location_use_case(
        self, session: AsyncSession
    ) -> UpdateUserLocationUseCase:
        """Provide UpdateUserLocationUseCase with dependencies."""
        card_repo = CardRepositoryImpl(session)
        return UpdateUserLocationUseCase(card_repository=card_repo)

    # Friend Use Cases
    @provider
    def provide_send_friend_request_use_case(
        self, session: AsyncSession
    ) -> SendFriendRequestUseCase:
        """Provide SendFriendRequestUseCase with dependencies."""
        friendship_repo = FriendshipRepositoryImpl(session)
        return SendFriendRequestUseCase(friendship_repository=friendship_repo)

    @provider
    def provide_accept_friend_request_use_case(
        self, session: AsyncSession
    ) -> AcceptFriendRequestUseCase:
        """Provide AcceptFriendRequestUseCase with dependencies."""
        friendship_repo = FriendshipRepositoryImpl(session)
        chat_room_repo = ChatRoomRepositoryImpl(session)
        return AcceptFriendRequestUseCase(
            friendship_repository=friendship_repo, chat_room_repository=chat_room_repo
        )

    @provider
    def provide_block_user_use_case(self, session: AsyncSession) -> BlockUserUseCase:
        """Provide BlockUserUseCase with dependencies."""
        friendship_repo = FriendshipRepositoryImpl(session)
        return BlockUserUseCase(friendship_repository=friendship_repo)

    # Chat Use Cases
    @provider
    def provide_send_message_use_case(
        self, session: AsyncSession
    ) -> SendMessageUseCase:
        """Provide SendMessageUseCase with dependencies."""
        chat_room_repo = ChatRoomRepositoryImpl(session)
        return SendMessageUseCase(chat_room_repository=chat_room_repo)

    @provider
    def provide_get_messages_use_case(
        self, session: AsyncSession
    ) -> GetMessagesUseCase:
        """Provide GetMessagesUseCase with dependencies."""
        chat_room_repo = ChatRoomRepositoryImpl(session)
        return GetMessagesUseCase(chat_room_repository=chat_room_repo)

    # Rating Use Cases
    @provider
    def provide_rate_user_use_case(self, session: AsyncSession) -> RateUserUseCase:
        """Provide RateUserUseCase with dependencies."""
        rating_repo = RatingRepositoryImpl(session)
        trade_repo = TradeRepositoryImpl(session)
        return RateUserUseCase(
            rating_repository=rating_repo, trade_repository=trade_repo
        )

    # Report Use Cases
    @provider
    def provide_report_user_use_case(self, session: AsyncSession) -> ReportUserUseCase:
        """Provide ReportUserUseCase with dependencies."""
        report_repo = ReportRepositoryImpl(session)
        return ReportUserUseCase(report_repository=report_repo)

    # Trade Use Cases
    @provider
    def provide_create_trade_proposal_use_case(
        self, session: AsyncSession
    ) -> CreateTradeProposalUseCase:
        """Provide CreateTradeProposalUseCase with dependencies."""
        trade_repo = TradeRepositoryImpl(session)
        card_repo = CardRepositoryImpl(session)
        friendship_repo = FriendshipRepositoryImpl(session)
        return CreateTradeProposalUseCase(
            trade_repository=trade_repo,
            card_repository=card_repo,
            friendship_repository=friendship_repo,
        )

    @provider
    def provide_accept_trade_use_case(
        self, session: AsyncSession
    ) -> AcceptTradeUseCase:
        """Provide AcceptTradeUseCase with dependencies."""
        trade_repo = TradeRepositoryImpl(session)
        return AcceptTradeUseCase(trade_repository=trade_repo)

    @provider
    def provide_reject_trade_use_case(
        self, session: AsyncSession
    ) -> RejectTradeUseCase:
        """Provide RejectTradeUseCase with dependencies."""
        trade_repo = TradeRepositoryImpl(session)
        return RejectTradeUseCase(trade_repository=trade_repo)

    @provider
    def provide_cancel_trade_use_case(
        self, session: AsyncSession
    ) -> CancelTradeUseCase:
        """Provide CancelTradeUseCase with dependencies."""
        trade_repo = TradeRepositoryImpl(session)
        return CancelTradeUseCase(trade_repository=trade_repo)

    @provider
    def provide_complete_trade_use_case(
        self, session: AsyncSession
    ) -> CompleteTradeUseCase:
        """Provide CompleteTradeUseCase with dependencies."""
        trade_repo = TradeRepositoryImpl(session)
        card_repo = CardRepositoryImpl(session)
        return CompleteTradeUseCase(
            trade_repository=trade_repo, card_repository=card_repo
        )

    @provider
    def provide_get_trade_history_use_case(
        self, session: AsyncSession
    ) -> GetTradeHistoryUseCase:
        """Provide GetTradeHistoryUseCase with dependencies."""
        trade_repo = TradeRepositoryImpl(session)
        return GetTradeHistoryUseCase(trade_repository=trade_repo)

    # Shared Contract Services - For cross-bounded-context communication
    @provider
    def provide_friendship_service(self, session: AsyncSession) -> IFriendshipService:
        """Provide IFriendshipService implementation."""
        friendship_repo = FriendshipRepositoryImpl(session)
        return FriendshipServiceImpl(friendship_repository=friendship_repo)

    @provider
    def provide_chat_room_service(self, session: AsyncSession) -> IChatRoomService:
        """Provide IChatRoomService implementation."""
        chat_room_repo = ChatRoomRepositoryImpl(session)
        return ChatRoomServiceImpl(chat_room_repository=chat_room_repo)
