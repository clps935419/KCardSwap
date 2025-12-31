"""Accept Interest Use Case - Accept an interest and create friendship + chat room"""

import uuid
from datetime import datetime, timezone

from app.modules.posts.domain.repositories.i_post_interest_repository import (
    IPostInterestRepository,
)
from app.modules.posts.domain.repositories.i_post_repository import IPostRepository
from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.domain.repositories.i_chat_room_repository import (
    IChatRoomRepository,
)
from app.modules.social.domain.repositories.i_friendship_repository import (
    IFriendshipRepository,
)


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
        friendship_repository: IFriendshipRepository,
        chat_room_repository: IChatRoomRepository,
    ):
        self.post_repository = post_repository
        self.post_interest_repository = post_interest_repository
        self.friendship_repository = friendship_repository
        self.chat_room_repository = chat_room_repository

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

        friendship_created = False
        existing_friendship = await self.friendship_repository.get_by_users(
            post_owner_id, interested_user_id
        )

        if not existing_friendship:
            # Create bidirectional friendship (both directions)
            # Create friendship from owner to interested user
            friendship1 = Friendship(
                id=str(uuid.uuid4()),
                user_id=post_owner_id,
                friend_id=interested_user_id,
                status=FriendshipStatus.ACCEPTED,
                created_at=datetime.now(timezone.utc),
            )
            await self.friendship_repository.create(friendship1)

            # Create friendship from interested user to owner
            friendship2 = Friendship(
                id=str(uuid.uuid4()),
                user_id=interested_user_id,
                friend_id=post_owner_id,
                status=FriendshipStatus.ACCEPTED,
                created_at=datetime.now(timezone.utc),
            )
            await self.friendship_repository.create(friendship2)

            friendship_created = True
        elif existing_friendship.status == FriendshipStatus.PENDING:
            # Auto-accept pending friendship
            existing_friendship.accept()
            await self.friendship_repository.update(existing_friendship)
            friendship_created = True

        # Get or create chat room
        chat_room = await self.chat_room_repository.get_by_participants(
            post_owner_id, interested_user_id
        )

        if not chat_room:
            chat_room = ChatRoom(
                id=str(uuid.uuid4()),
                participant_ids=[post_owner_id, interested_user_id],
                created_at=datetime.now(timezone.utc),
            )
            chat_room = await self.chat_room_repository.create(chat_room)

        return AcceptInterestResult(
            interest_id=interest_id,
            friendship_created=friendship_created,
            chat_room_id=chat_room.id,
        )
