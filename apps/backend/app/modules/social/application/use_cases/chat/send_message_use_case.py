"""Send Message Use Case"""

import uuid
from datetime import datetime
from typing import Optional

from app.modules.social.domain.entities.message import Message, MessageStatus
from app.modules.social.domain.repositories.chat_room_repository import (
    ChatRoomRepository,
)
from app.modules.social.domain.repositories.friendship_repository import (
    FriendshipRepository,
)
from app.modules.social.domain.repositories.message_repository import MessageRepository


class SendMessageUseCase:
    """
    Use case for sending a chat message

    Business Rules:
    - Users must be friends to send messages
    - Users cannot send messages if either has blocked the other
    - Chat room must exist
    - Message triggers FCM push notification (handled by presentation layer)

    Note: FCM notification triggering is handled after successful message creation
    in the presentation layer (router), not in this use case. This keeps the
    use case focused on business logic.
    """

    def __init__(
        self,
        message_repository: MessageRepository,
        chat_room_repository: ChatRoomRepository,
        friendship_repository: FriendshipRepository,
    ):
        self.message_repository = message_repository
        self.chat_room_repository = chat_room_repository
        self.friendship_repository = friendship_repository

    async def execute(self, room_id: str, sender_id: str, content: str) -> Message:
        """
        Send a message in a chat room

        Args:
            room_id: ID of the chat room
            sender_id: ID of the user sending the message
            content: Message content

        Returns:
            Created Message entity

        Raises:
            ValueError: If chat room doesn't exist, user not authorized, or blocked
        """
        # Verify chat room exists
        chat_room = await self.chat_room_repository.get_by_id(room_id)
        if not chat_room:
            raise ValueError("Chat room not found")

        # Verify sender is a participant
        if not chat_room.has_participant(sender_id):
            raise ValueError("User is not a participant in this chat room")

        # Get the other participant
        recipient_id = chat_room.get_other_participant(sender_id)

        # Verify users are friends and not blocked
        if not await self.friendship_repository.are_friends(sender_id, recipient_id):
            raise ValueError("Users must be friends to send messages")

        if await self.friendship_repository.is_blocked(sender_id, recipient_id):
            raise ValueError("Cannot send message - user is blocked")

        # Create message
        message = Message(
            id=str(uuid.uuid4()),
            room_id=room_id,
            sender_id=sender_id,
            content=content,
            status=MessageStatus.SENT,
            created_at=datetime.utcnow(),
        )

        return await self.message_repository.create(message)
