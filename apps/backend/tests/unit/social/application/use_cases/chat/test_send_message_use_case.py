"""
Unit tests for SendMessageUseCase
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.modules.social.application.use_cases.chat.send_message_use_case import (
    SendMessageUseCase,
)
from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.entities.message import MessageStatus


class TestSendMessageUseCase:
    """Test SendMessageUseCase"""

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
        return SendMessageUseCase(
            message_repository=mock_message_repository,
            chat_room_repository=mock_chat_room_repository,
            friendship_repository=mock_friendship_repository,
        )

    @pytest.mark.asyncio
    async def test_send_message_success(
        self,
        use_case,
        mock_message_repository,
        mock_chat_room_repository,
        mock_friendship_repository,
    ):
        """Test successfully sending a message"""
        # Arrange
        room_id = "room-123"
        sender_id = "user-123"
        recipient_id = "user-456"
        content = "Hello, friend!"

        # Mock chat room exists with both participants
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[sender_id, recipient_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends and not blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = False

        # Mock create to return message
        def create_side_effect(message):
            return message

        mock_message_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(room_id, sender_id, content)

        # Assert
        assert result is not None
        assert result.room_id == room_id
        assert result.sender_id == sender_id
        assert result.content == content
        assert result.status == MessageStatus.SENT

        # Verify repository calls
        mock_chat_room_repository.get_by_id.assert_called_once_with(room_id)
        mock_friendship_repository.are_friends.assert_called_once_with(
            sender_id, recipient_id
        )
        mock_friendship_repository.is_blocked.assert_called_once_with(
            sender_id, recipient_id
        )
        mock_message_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_chat_room_not_found(
        self, use_case, mock_chat_room_repository, mock_message_repository
    ):
        """Test error when chat room doesn't exist"""
        # Arrange
        room_id = "room-123"
        sender_id = "user-123"
        content = "Hello!"

        # Mock no chat room found
        mock_chat_room_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Chat room not found"):
            await use_case.execute(room_id, sender_id, content)

        # Verify no message was created
        mock_message_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_message_sender_not_participant(
        self,
        use_case,
        mock_chat_room_repository,
        mock_message_repository,
    ):
        """Test error when sender is not a participant"""
        # Arrange
        room_id = "room-123"
        sender_id = "user-123"
        other_user = "user-456"
        third_user = "user-789"
        content = "Hello!"

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
            await use_case.execute(room_id, sender_id, content)

        # Verify no message was created
        mock_message_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_message_users_not_friends(
        self,
        use_case,
        mock_chat_room_repository,
        mock_friendship_repository,
        mock_message_repository,
    ):
        """Test error when users are not friends"""
        # Arrange
        room_id = "room-123"
        sender_id = "user-123"
        recipient_id = "user-456"
        content = "Hello!"

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[sender_id, recipient_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are not friends
        mock_friendship_repository.are_friends.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match="Users must be friends to send messages"):
            await use_case.execute(room_id, sender_id, content)

        # Verify no message was created
        mock_message_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_message_user_blocked(
        self,
        use_case,
        mock_chat_room_repository,
        mock_friendship_repository,
        mock_message_repository,
    ):
        """Test error when user is blocked"""
        # Arrange
        room_id = "room-123"
        sender_id = "user-123"
        recipient_id = "user-456"
        content = "Hello!"

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[sender_id, recipient_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends but blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot send message - user is blocked"):
            await use_case.execute(room_id, sender_id, content)

        # Verify no message was created
        mock_message_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_message_empty_content(
        self,
        use_case,
        mock_chat_room_repository,
        mock_friendship_repository,
        mock_message_repository,
    ):
        """Test that message validation happens in Message entity"""
        # Arrange
        room_id = "room-123"
        sender_id = "user-123"
        recipient_id = "user-456"
        content = ""  # Empty content

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[sender_id, recipient_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends and not blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = False

        # Act & Assert
        # The Message entity itself validates empty content
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            await use_case.execute(room_id, sender_id, content)

    @pytest.mark.asyncio
    async def test_send_message_long_content(
        self,
        use_case,
        mock_chat_room_repository,
        mock_friendship_repository,
        mock_message_repository,
    ):
        """Test sending message with valid long content"""
        # Arrange
        room_id = "room-123"
        sender_id = "user-123"
        recipient_id = "user-456"
        content = "A" * 1000  # Long but valid content (under 5000 limit)

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[sender_id, recipient_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends and not blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = False

        # Mock create to return message
        def create_side_effect(message):
            return message

        mock_message_repository.create.side_effect = create_side_effect

        # Act
        result = await use_case.execute(room_id, sender_id, content)

        # Assert
        assert result is not None
        assert result.content == content
        assert len(result.content) == 1000

    @pytest.mark.asyncio
    async def test_send_message_exceeds_max_length(
        self,
        use_case,
        mock_chat_room_repository,
        mock_friendship_repository,
    ):
        """Test that message exceeding max length is rejected by Message entity"""
        # Arrange
        room_id = "room-123"
        sender_id = "user-123"
        recipient_id = "user-456"
        content = "A" * 6000  # Exceeds 5000 character limit

        # Mock chat room exists
        chat_room = ChatRoom(
            id=room_id,
            participant_ids=[sender_id, recipient_id],
            created_at=datetime.utcnow(),
        )
        mock_chat_room_repository.get_by_id.return_value = chat_room

        # Mock users are friends and not blocked
        mock_friendship_repository.are_friends.return_value = True
        mock_friendship_repository.is_blocked.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match="Message content exceeds maximum length"):
            await use_case.execute(room_id, sender_id, content)
