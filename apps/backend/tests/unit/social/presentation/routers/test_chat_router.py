"""
Unit tests for Chat Router

Tests the chat router endpoints with mocked use cases.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.modules.social.domain.entities.message import MessageStatus
from app.modules.social.presentation.routers.chat_router import (
    get_chat_rooms,
    get_messages,
    mark_message_read,
    send_message,
)
from app.modules.social.presentation.schemas.chat_schemas import (
    SendMessageRequest,
)


class TestChatRouter:
    """Test Chat Router endpoints"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        return AsyncMock()

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_room_id(self):
        """Create sample room ID"""
        return uuid4()

    @pytest.fixture
    def sample_message_id(self):
        """Create sample message ID"""
        return uuid4()

    @pytest.fixture
    def sample_friend_id(self):
        """Create sample friend ID"""
        return uuid4()

    @pytest.fixture
    def mock_chat_room(self, sample_room_id, sample_user_id, sample_friend_id):
        """Create mock chat room entity"""
        room = MagicMock()
        room.id = str(sample_room_id)
        room.participant_ids = [str(sample_user_id), str(sample_friend_id)]
        room.created_at = datetime.now(timezone.utc)
        room.has_participant = MagicMock(return_value=True)
        room.get_other_participant = MagicMock(return_value=str(sample_friend_id))
        return room

    @pytest.fixture
    def mock_message(self, sample_message_id, sample_room_id, sample_user_id):
        """Create mock message entity"""
        message = MagicMock()
        message.id = str(sample_message_id)
        message.room_id = str(sample_room_id)
        message.sender_id = str(sample_user_id)
        message.content = "Hello, this is a test message"
        message.status = MessageStatus.SENT
        message.created_at = datetime.now(timezone.utc)
        message.mark_read = MagicMock()
        return message

    # Tests for GET /chats
    @pytest.mark.asyncio
    async def test_get_chat_rooms_success(
        self,
        mock_session,
        sample_user_id,
        mock_chat_room,
    ):
        """Test successful retrieval of chat rooms"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_rooms_by_user_id.return_value = [mock_chat_room]
            mock_repo_class.return_value = mock_repo

            # Act
            response = await get_chat_rooms(
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert response.data is not None
            assert response.data.total == 1
            assert len(response.data.rooms) == 1
            assert response.data.rooms[0].id == UUID(mock_chat_room.id)
            assert response.error is None
            mock_repo.get_rooms_by_user_id.assert_called_once_with(str(sample_user_id))

    @pytest.mark.asyncio
    async def test_get_chat_rooms_empty_list(
        self,
        mock_session,
        sample_user_id,
    ):
        """Test retrieval of chat rooms when user has no rooms"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_rooms_by_user_id.return_value = []
            mock_repo_class.return_value = mock_repo

            # Act
            response = await get_chat_rooms(
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert response.data is not None
            assert response.data.total == 0
            assert len(response.data.rooms) == 0
            assert response.error is None

    @pytest.mark.asyncio
    async def test_get_chat_rooms_with_multiple_rooms(
        self,
        mock_session,
        sample_user_id,
        mock_chat_room,
    ):
        """Test retrieval of multiple chat rooms"""
        # Arrange
        room2 = MagicMock()
        room2.id = str(uuid4())
        room2.participant_ids = [str(sample_user_id), str(uuid4())]
        room2.created_at = datetime.now(timezone.utc)

        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_rooms_by_user_id.return_value = [mock_chat_room, room2]
            mock_repo_class.return_value = mock_repo

            # Act
            response = await get_chat_rooms(
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert response.data is not None
            assert response.data.total == 2
            assert len(response.data.rooms) == 2

    @pytest.mark.asyncio
    async def test_get_chat_rooms_error_handling(
        self,
        mock_session,
        sample_user_id,
    ):
        """Test error handling in get_chat_rooms"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_rooms_by_user_id.side_effect = Exception("Database error")
            mock_repo_class.return_value = mock_repo

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_chat_rooms(
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 500
            assert "Failed to get chat rooms" in str(exc_info.value.detail)

    # Tests for GET /chats/{room_id}/messages
    @pytest.mark.asyncio
    async def test_get_messages_success(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        mock_message,
    ):
        """Test successful retrieval of messages"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.chat_router.GetMessagesUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = [mock_message]
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_messages(
                room_id=sample_room_id,
                current_user_id=sample_user_id,
                session=mock_session,
                after_message_id=None,
                limit=50,
            )

            # Assert
            assert response.data is not None
            assert response.data.total == 1
            assert len(response.data.messages) == 1
            assert response.data.messages[0].id == UUID(mock_message.id)
            assert response.data.messages[0].content == mock_message.content
            assert response.error is None
            mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_messages_with_pagination(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        mock_message,
    ):
        """Test retrieval of messages with pagination"""
        # Arrange
        after_message_id = uuid4()

        with patch(
            "app.modules.social.presentation.routers.chat_router.GetMessagesUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = [mock_message]
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_messages(
                room_id=sample_room_id,
                current_user_id=sample_user_id,
                session=mock_session,
                after_message_id=after_message_id,
                limit=20,
            )

            # Assert
            assert response.data is not None
            mock_use_case.execute.assert_called_once_with(
                room_id=str(sample_room_id),
                requesting_user_id=str(sample_user_id),
                after_message_id=str(after_message_id),
                limit=20,
            )

    @pytest.mark.asyncio
    async def test_get_messages_room_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
    ):
        """Test get messages when room not found"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.chat_router.GetMessagesUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Chat room not found")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_messages(
                    room_id=sample_room_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                    after_message_id=None,
                    limit=50,
                )

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_messages_not_participant(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
    ):
        """Test get messages when user is not a participant"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.chat_router.GetMessagesUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Not a participant of this room")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_messages(
                    room_id=sample_room_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                    after_message_id=None,
                    limit=50,
                )

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_messages_has_more_flag(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        mock_message,
    ):
        """Test has_more flag when limit is reached"""
        # Arrange
        messages = [mock_message] * 50  # Exactly limit count

        with patch(
            "app.modules.social.presentation.routers.chat_router.GetMessagesUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = messages
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_messages(
                room_id=sample_room_id,
                current_user_id=sample_user_id,
                session=mock_session,
                after_message_id=None,
                limit=50,
            )

            # Assert
            assert response.data.has_more is True

    # Tests for POST /chats/{room_id}/messages
    @pytest.mark.asyncio
    async def test_send_message_success(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        mock_message,
        mock_chat_room,
    ):
        """Test successful message sending"""
        # Arrange
        request = SendMessageRequest(content="Hello, friend!")

        with patch(
            "app.modules.social.presentation.routers.chat_router.SendMessageUseCase"
        ) as mock_use_case_class, patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_repo_class, patch(
            "app.modules.social.presentation.routers.chat_router.get_fcm_service"
        ) as mock_fcm_service:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_message
            mock_use_case_class.return_value = mock_use_case

            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_chat_room
            mock_repo_class.return_value = mock_repo

            mock_fcm = AsyncMock()
            mock_fcm_service.return_value = mock_fcm

            # Act
            response = await send_message(
                room_id=sample_room_id,
                request=request,
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert response.data is not None
            assert response.data.id == UUID(mock_message.id)
            assert response.data.content == mock_message.content
            assert response.error is None
            mock_use_case.execute.assert_called_once_with(
                room_id=str(sample_room_id),
                sender_id=str(sample_user_id),
                content="Hello, friend!",
            )

    @pytest.mark.asyncio
    async def test_send_message_room_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
    ):
        """Test send message when room not found"""
        # Arrange
        request = SendMessageRequest(content="Hello")

        with patch(
            "app.modules.social.presentation.routers.chat_router.SendMessageUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Chat room not found")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await send_message(
                    room_id=sample_room_id,
                    request=request,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_send_message_not_authorized(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
    ):
        """Test send message when user not authorized"""
        # Arrange
        request = SendMessageRequest(content="Hello")

        with patch(
            "app.modules.social.presentation.routers.chat_router.SendMessageUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Not authorized to send message")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await send_message(
                    room_id=sample_room_id,
                    request=request,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_send_message_blocked_user(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
    ):
        """Test send message when user is blocked"""
        # Arrange
        request = SendMessageRequest(content="Hello")

        with patch(
            "app.modules.social.presentation.routers.chat_router.SendMessageUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("User is blocked")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await send_message(
                    room_id=sample_room_id,
                    request=request,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_fcm_notification_sent(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        mock_message,
        mock_chat_room,
        sample_friend_id,
    ):
        """Test that FCM notification is sent after message creation"""
        # Arrange
        request = SendMessageRequest(content="Hello, friend!")

        with patch(
            "app.modules.social.presentation.routers.chat_router.SendMessageUseCase"
        ) as mock_use_case_class, patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_repo_class, patch(
            "app.modules.social.presentation.routers.chat_router.get_fcm_service"
        ) as mock_fcm_service:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_message
            mock_use_case_class.return_value = mock_use_case

            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_chat_room
            mock_repo_class.return_value = mock_repo

            mock_fcm = AsyncMock()
            mock_fcm_service.return_value = mock_fcm

            # Act
            await send_message(
                room_id=sample_room_id,
                request=request,
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            mock_fcm.send_notification.assert_called_once()
            call_args = mock_fcm.send_notification.call_args[1]
            assert call_args["user_id"] == str(sample_friend_id)
            assert call_args["title"] == "New message"
            # The body uses the actual message content from mock_message
            assert mock_message.content[:50] in call_args["body"]

    @pytest.mark.asyncio
    async def test_send_message_fcm_failure_does_not_fail_request(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        mock_message,
        mock_chat_room,
    ):
        """Test that FCM notification failure does not fail the message sending"""
        # Arrange
        request = SendMessageRequest(content="Hello")

        with patch(
            "app.modules.social.presentation.routers.chat_router.SendMessageUseCase"
        ) as mock_use_case_class, patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_repo_class, patch(
            "app.modules.social.presentation.routers.chat_router.get_fcm_service"
        ) as mock_fcm_service:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_message
            mock_use_case_class.return_value = mock_use_case

            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_chat_room
            mock_repo_class.return_value = mock_repo

            mock_fcm = AsyncMock()
            mock_fcm.send_notification.side_effect = Exception("FCM error")
            mock_fcm_service.return_value = mock_fcm

            # Act - Should not raise exception
            response = await send_message(
                room_id=sample_room_id,
                request=request,
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert response.data is not None
            assert response.data.content == mock_message.content

    # Tests for POST /chats/{room_id}/messages/{message_id}/read
    @pytest.mark.asyncio
    async def test_mark_message_read_success(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        sample_message_id,
        mock_chat_room,
        mock_message,
        sample_friend_id,
    ):
        """Test successful marking of message as read"""
        # Arrange
        mock_message.sender_id = str(sample_friend_id)  # Not the current user
        mock_message.status = MessageStatus.SENT

        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_room_repo_class, patch(
            "app.modules.social.presentation.routers.chat_router.MessageRepositoryImpl"
        ) as mock_msg_repo_class:
            mock_room_repo = AsyncMock()
            mock_room_repo.get_by_id.return_value = mock_chat_room
            mock_room_repo_class.return_value = mock_room_repo

            mock_msg_repo = AsyncMock()
            mock_msg_repo.get_by_id.return_value = mock_message
            mock_msg_repo.update = AsyncMock()
            mock_msg_repo_class.return_value = mock_msg_repo

            # Act
            result = await mark_message_read(
                room_id=sample_room_id,
                message_id=sample_message_id,
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert result is None  # 204 No Content
            mock_message.mark_read.assert_called_once()
            mock_msg_repo.update.assert_called_once_with(mock_message)

    @pytest.mark.asyncio
    async def test_mark_message_read_room_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        sample_message_id,
    ):
        """Test mark message as read when room not found"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_room_repo_class:
            mock_room_repo = AsyncMock()
            mock_room_repo.get_by_id.return_value = None
            mock_room_repo_class.return_value = mock_room_repo

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await mark_message_read(
                    room_id=sample_room_id,
                    message_id=sample_message_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 404
            assert "Chat room not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_mark_message_read_not_participant(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        sample_message_id,
        mock_chat_room,
    ):
        """Test mark message as read when user is not participant"""
        # Arrange
        mock_chat_room.has_participant.return_value = False

        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_room_repo_class:
            mock_room_repo = AsyncMock()
            mock_room_repo.get_by_id.return_value = mock_chat_room
            mock_room_repo_class.return_value = mock_room_repo

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await mark_message_read(
                    room_id=sample_room_id,
                    message_id=sample_message_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 403
            assert "Not authorized" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_mark_message_read_message_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        sample_message_id,
        mock_chat_room,
    ):
        """Test mark message as read when message not found"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_room_repo_class, patch(
            "app.modules.social.presentation.routers.chat_router.MessageRepositoryImpl"
        ) as mock_msg_repo_class:
            mock_room_repo = AsyncMock()
            mock_room_repo.get_by_id.return_value = mock_chat_room
            mock_room_repo_class.return_value = mock_room_repo

            mock_msg_repo = AsyncMock()
            mock_msg_repo.get_by_id.return_value = None
            mock_msg_repo_class.return_value = mock_msg_repo

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await mark_message_read(
                    room_id=sample_room_id,
                    message_id=sample_message_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 404
            assert "Message not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_mark_message_read_own_message(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        sample_message_id,
        mock_chat_room,
        mock_message,
    ):
        """Test mark message as read when trying to mark own message"""
        # Arrange
        mock_message.sender_id = str(sample_user_id)  # Same as current user

        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_room_repo_class, patch(
            "app.modules.social.presentation.routers.chat_router.MessageRepositoryImpl"
        ) as mock_msg_repo_class:
            mock_room_repo = AsyncMock()
            mock_room_repo.get_by_id.return_value = mock_chat_room
            mock_room_repo_class.return_value = mock_room_repo

            mock_msg_repo = AsyncMock()
            mock_msg_repo.get_by_id.return_value = mock_message
            mock_msg_repo_class.return_value = mock_msg_repo

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await mark_message_read(
                    room_id=sample_room_id,
                    message_id=sample_message_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 422
            assert "Cannot mark your own message as read" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_mark_message_read_already_read(
        self,
        mock_session,
        sample_user_id,
        sample_room_id,
        sample_message_id,
        mock_chat_room,
        mock_message,
        sample_friend_id,
    ):
        """Test mark message as read when already read"""
        # Arrange
        mock_message.sender_id = str(sample_friend_id)
        mock_message.status = MessageStatus.READ  # Already read

        with patch(
            "app.modules.social.presentation.routers.chat_router.ChatRoomRepositoryImpl"
        ) as mock_room_repo_class, patch(
            "app.modules.social.presentation.routers.chat_router.MessageRepositoryImpl"
        ) as mock_msg_repo_class:
            mock_room_repo = AsyncMock()
            mock_room_repo.get_by_id.return_value = mock_chat_room
            mock_room_repo_class.return_value = mock_room_repo

            mock_msg_repo = AsyncMock()
            mock_msg_repo.get_by_id.return_value = mock_message
            mock_msg_repo.update = AsyncMock()
            mock_msg_repo_class.return_value = mock_msg_repo

            # Act
            result = await mark_message_read(
                room_id=sample_room_id,
                message_id=sample_message_id,
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert result is None  # Still returns success
            mock_message.mark_read.assert_not_called()  # But doesn't update
            mock_msg_repo.update.assert_not_called()
