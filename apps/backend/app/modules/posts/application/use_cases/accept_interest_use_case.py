"""Accept Interest Use Case - Accept an interest and create friendship + chat room"""

from uuid import UUID

from app.modules.posts.domain.repositories.i_post_interest_repository import (
    IPostInterestRepository,
)
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository
from app.shared.domain.contracts.i_chat_room_service import IChatRoomService
from app.shared.domain.contracts.i_friendship_service import IFriendshipService


class AcceptInterestResult:
    """Result of accepting an interest"""

    def __init__(self, interest_id: str, friendship_created: bool, chat_room_id: str):
        self.interest_id = interest_id
        self.friendship_created = friendship_created
        self.chat_room_id = chat_room_id


class AcceptInterestUseCase:
    """
    Use case for accepting an interest in a post

    Business Rules:
    - Only post owner can accept interests
    - Interest must be pending
    - Automatically create friendship if not already friends
    - Create or reuse existing chat room
    """

    def __init__(
        self,
        post_repository: IPostRepository,
        post_interest_repository: IPostInterestRepository,
        friendship_repository: IFriendshipService,
        chat_room_repository: IChatRoomService,
    ):
        self.post_repository = post_repository
        self.post_interest_repository = post_interest_repository
        self.friendship_service = friendship_repository
        self.chat_room_service = chat_room_repository

    async def execute(
        self, post_id: str, interest_id: str, current_user_id: str
    ) -> AcceptInterestResult:
        """
        Accept an interest

        Args:
            post_id: ID of the post
            interest_id: ID of the interest to accept
            current_user_id: ID of the current user (must be post owner)

        Returns:
            AcceptInterestResult with details of created/reused resources

        Raises:
            ValueError: If validation fails
        """
        # Get post
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            raise ValueError("Post not found")

        # Validate: only post owner can accept
        if post.owner_id != current_user_id:
            raise ValueError("Only post owner can accept interests")

        # Get interest
        interest = await self.post_interest_repository.get_by_id(interest_id)
        if not interest:
            raise ValueError("Interest not found")

        # Validate: interest belongs to this post
        if interest.post_id != post_id:
            raise ValueError("Interest does not belong to this post")

        # Validate: interest must be pending
        if not interest.is_pending():
            raise ValueError(f"Interest is already {interest.status}")

        # Accept the interest
        interest.accept()
        await self.post_interest_repository.update(interest)

        # Check if already friends
        interested_user_id = interest.user_id
        post_owner_id = post.owner_id

        # Convert string IDs to UUIDs
        interested_uuid = UUID(interested_user_id)
        owner_uuid = UUID(post_owner_id)

        friendship_created = False
        existing_friendship = await self.friendship_service.get_friendship(
            owner_uuid, interested_uuid
        )

        if not existing_friendship:
            # Create friendship (service handles it automatically as accepted)
            await self.friendship_service.create_friendship(
                owner_uuid, interested_uuid, auto_accept=True
            )
            friendship_created = True

        # Get or create chat room using the service
        chat_room_dto = await self.chat_room_service.get_or_create_chat_room(
            owner_uuid, interested_uuid
        )

        return AcceptInterestResult(
            interest_id=interest_id,
            friendship_created=friendship_created,
            chat_room_id=str(chat_room_dto.id),
        )
