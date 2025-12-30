"""
Unit tests for GetMessagesUseCase
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.modules.social.application.use_cases.chat.get_messages_use_case import (
    GetMessagesUseCase,
)
from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.entities.message import Message, MessageStatus


class TestGetMessagesUseCase:
    """Test GetMessagesUseCase"""

    @pytest.fixture
    def mock_message_repository(self):
        """Create mock message repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_chat_room_repository(self):
        """Create mock chat room repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_friendship_repository(self):
        """Create mock friendship repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(
        self,
        mock_message_repository,
        mock_chat_room_repository,
        mock_friendship_repository,
    ):
        """Create use case instance"""
        return GetMessagesUseCase(
            message_repository=mock_message_repository,
            chat_room_repository=mock_chat_room_repository,
            friendship_repository=mock_friendship_repository,
        )

    @pytest.mark.asyncio
    async def test_get_messages_success(
        self,
        use_case,
        mock_message_repository,
        mock_chat_room_repository,
        mock_friendship_repository,
    ):
        """Test successfully retrieving messages"""
        # Arrange
        room_id = "room-123"
        user_id = "user-123"
        other_user_id = "user-456"

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[user_id, other_user_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends and not blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = False

        # Mock messages
        messages = [
            Message(
                id="msg-1",
                room_id=room_id,
                sender_id=user_id,
                content="Hello",
                status=MessageStatus.SENT,
                created_at=datetime.utcnow(),
            ),
            Message(
                id="msg-2",
                room_id=room_id,
                sender_id=other_user_id,
                content="Hi there",
                status=MessageStatus.SENT,
                created_at=datetime.utcnow(),
            ),
        ]
        mock_message_repository.get_messages_by_room_id.return_value = messages

        # Act
        result = await use_case.execute(
            room_id=room_id, requesting_user_id=user_id, after_message_id=None, limit=50
        )

        # Assert
        assert result is not None
        assert len(result) == 2
        assert result == messages

        # Verify repository calls
        mock_chat_room_repository.get_by_id.assert_called_once_with(room_id)
        mock_friendship_repository.are_friends.assert_called_once_with(
            user_id, other_user_id
        )
        mock_friendship_repository.is_blocked.assert_called_once_with(
            user_id, other_user_id
        )
        mock_message_repository.get_messages_by_room_id.assert_called_once_with(
            room_id=room_id, after_message_id=None, limit=50
        )

    @pytest.mark.asyncio
    async def test_get_messages_with_cursor(
        self,
        use_case,
        mock_message_repository,
        mock_chat_room_repository,
        mock_friendship_repository,
    ):
        """Test retrieving messages with cursor-based pagination"""
        # Arrange
        room_id = "room-123"
        user_id = "user-123"
        other_user_id = "user-456"
        after_message_id = "msg-1"

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[user_id, other_user_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends and not blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = False

        # Mock new messages after cursor
        messages = [
            Message(
                id="msg-2",
                room_id=room_id,
                sender_id=other_user_id,
                content="New message",
                status=MessageStatus.SENT,
                created_at=datetime.utcnow(),
            )
        ]
        mock_message_repository.get_messages_by_room_id.return_value = messages

        # Act
        result = await use_case.execute(
            room_id=room_id,
            requesting_user_id=user_id,
            after_message_id=after_message_id,
            limit=50,
        )

        # Assert
        assert result is not None
        assert len(result) == 1

        # Verify repository calls with cursor
        mock_message_repository.get_messages_by_room_id.assert_called_once_with(
            room_id=room_id, after_message_id=after_message_id, limit=50
        )

    @pytest.mark.asyncio
    async def test_get_messages_with_custom_limit(
        self,
        use_case,
        mock_message_repository,
        mock_chat_room_repository,
        mock_friendship_repository,
    ):
        """Test retrieving messages with custom limit"""
        # Arrange
        room_id = "room-123"
        user_id = "user-123"
        other_user_id = "user-456"
        limit = 10

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[user_id, other_user_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends and not blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = False

        # Mock limited messages
        mock_message_repository.get_messages_by_room_id.return_value = []

        # Act
        result = await use_case.execute(
            room_id=room_id,
            requesting_user_id=user_id,
            after_message_id=None,
            limit=limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, list)

        # Verify repository calls with custom limit
        mock_message_repository.get_messages_by_room_id.assert_called_once_with(
            room_id=room_id, after_message_id=None, limit=limit
        )

    @pytest.mark.asyncio
    async def test_get_messages_chat_room_not_found(
        self, use_case, mock_chat_room_repository, mock_message_repository
    ):
        """Test error when chat room doesn't exist"""
        # Arrange
        room_id = "room-123"
        user_id = "user-123"

        # Mock no chat room found
        mock_chat_room_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Chat room not found"):
            await use_case.execute(
                room_id=room_id, requesting_user_id=user_id, after_message_id=None
            )

        # Verify no messages were retrieved
        mock_message_repository.get_messages_by_room_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_messages_user_not_participant(
        self, use_case, mock_chat_room_repository, mock_message_repository
    ):
        """Test error when user is not a participant"""
        # Arrange
        room_id = "room-123"
        user_id = "user-123"
        other_user = "user-456"
        third_user = "user-789"

        # Mock chat room with different participants
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[other_user, third_user],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Act & Assert
        with pytest.raises(
            ValueError, match="User is not a participant in this chat room"
        ):
            await use_case.execute(
                room_id=room_id, requesting_user_id=user_id, after_message_id=None
            )

        # Verify no messages were retrieved
        mock_message_repository.get_messages_by_room_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_messages_users_not_friends(
        self,
        use_case,
        mock_chat_room_repository,
        mock_friendship_repository,
        mock_message_repository,
    ):
        """Test error when users are not friends"""
        # Arrange
        room_id = "room-123"
        user_id = "user-123"
        other_user_id = "user-456"

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[user_id, other_user_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are not friends
        mock_friendship_repository.are_friends.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match="Users must be friends to access messages"):
            await use_case.execute(
                room_id=room_id, requesting_user_id=user_id, after_message_id=None
            )

        # Verify no messages were retrieved
        mock_message_repository.get_messages_by_room_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_messages_user_blocked(
        self,
        use_case,
        mock_chat_room_repository,
        mock_friendship_repository,
        mock_message_repository,
    ):
        """Test error when user is blocked"""
        # Arrange
        room_id = "room-123"
        user_id = "user-123"
        other_user_id = "user-456"

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[user_id, other_user_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends but blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot access messages - user is blocked"):
            await use_case.execute(
                room_id=room_id, requesting_user_id=user_id, after_message_id=None
            )

        # Verify no messages were retrieved
        mock_message_repository.get_messages_by_room_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_messages_empty_result(
        self,
        use_case,
        mock_message_repository,
        mock_chat_room_repository,
        mock_friendship_repository,
    ):
        """Test retrieving messages when no messages exist"""
        # Arrange
        room_id = "room-123"
        user_id = "user-123"
        other_user_id = "user-456"

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[user_id, other_user_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends and not blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = False

        # Mock no messages
        mock_message_repository.get_messages_by_room_id.return_value = []

        # Act
        result = await use_case.execute(
            room_id=room_id, requesting_user_id=user_id, after_message_id=None
        )

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0
