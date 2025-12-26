"""Get Messages Use Case"""
from typing import List, Optional

from app.modules.social.domain.entities.message import Message
from app.modules.social.domain.repositories.chat_room_repository import (
    ChatRoomRepository,
)
from app.modules.social.domain.repositories.friendship_repository import (
    FriendshipRepository,
)
from app.modules.social.domain.repositories.message_repository import MessageRepository


class GetMessagesUseCase:
    """
    Use case for retrieving messages with polling support

    Business Rules:
    - User must be a participant in the chat room
    - Users must be friends (not blocked)
    - Supports incremental polling using after_message_id cursor
    - Returns messages in ascending order by created_at

    Polling Mechanism:
    - Client provides after_message_id to get only new messages
    - If after_message_id is None, returns recent messages (up to limit)
    - Recommended polling interval: 3-5 seconds when chat screen is active
    - Client should implement backoff to avoid excessive API calls

    Message Retention:
    - Messages are retained for 30 days on server (FR-CHAT-006)
    - Cleanup job implementation is deferred (T125A)
    """

    def __init__(
        self,
        message_repository: MessageRepository,
        chat_room_repository: ChatRoomRepository,
        friendship_repository: FriendshipRepository
    ):
        self.message_repository = message_repository
        self.chat_room_repository = chat_room_repository
        self.friendship_repository = friendship_repository

    async def execute(
        self,
        room_id: str,
        requesting_user_id: str,
        after_message_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Message]:
        """
        Get messages for a chat room with optional cursor-based pagination

        Args:
            room_id: ID of the chat room
            requesting_user_id: ID of the user requesting messages
            after_message_id: Optional cursor - return messages after this ID
            limit: Maximum number of messages to return (default 50)

        Returns:
            List of Message entities ordered by created_at ascending

        Raises:
            ValueError: If user not authorized or chat room doesn't exist
        """
        # Verify chat room exists
        chat_room = await self.chat_room_repository.get_by_id(room_id)
        if not chat_room:
            raise ValueError("Chat room not found")

        # Verify user is a participant
        if not chat_room.has_participant(requesting_user_id):
            raise ValueError("User is not a participant in this chat room")

        # Get the other participant
        other_participant_id = chat_room.get_other_participant(requesting_user_id)

        # Verify users are still friends and not blocked
        if not await self.friendship_repository.are_friends(requesting_user_id, other_participant_id):
            raise ValueError("Users must be friends to access messages")

        if await self.friendship_repository.is_blocked(requesting_user_id, other_participant_id):
            raise ValueError("Cannot access messages - user is blocked")

        # Get messages with cursor-based pagination
        messages = await self.message_repository.get_messages_by_room_id(
            room_id=room_id,
            after_message_id=after_message_id,
            limit=limit
        )

        return messages
