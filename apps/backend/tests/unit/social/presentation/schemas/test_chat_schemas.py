"""
Unit tests for Chat Schemas
Testing Pydantic model validation and serialization
"""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.social.presentation.schemas.chat_schemas import (
    ChatRoomListResponse,
    ChatRoomListResponseWrapper,
    ChatRoomParticipantResponse,
    ChatRoomResponse,
    ChatRoomResponseWrapper,
    GetMessagesRequest,
    MessageResponse,
    MessageResponseWrapper,
    MessagesListResponse,
    MessagesListResponseWrapper,
    SendMessageRequest,
)


class TestSendMessageRequest:
    """Test SendMessageRequest schema"""

    def test_create_valid_request(self):
        """Test creating valid send message request"""
        request = SendMessageRequest(
            content="Hello! I'm interested in trading cards."
        )

        assert request.content == "Hello! I'm interested in trading cards."

    def test_empty_content_fails(self):
        """Test that empty content fails validation"""
        with pytest.raises(ValidationError):
            SendMessageRequest(content="")

    def test_content_too_long_fails(self):
        """Test that content over 2000 characters fails"""
        long_content = "a" * 2001
        with pytest.raises(ValidationError):
            SendMessageRequest(content=long_content)

    def test_max_length_content_succeeds(self):
        """Test that exactly 2000 characters succeeds"""
        max_content = "a" * 2000
        request = SendMessageRequest(content=max_content)

        assert len(request.content) == 2000

    def test_missing_content_fails(self):
        """Test that missing content fails validation"""
        with pytest.raises(ValidationError):
            SendMessageRequest()


class TestMessageResponse:
    """Test MessageResponse schema"""

    def test_create_valid_response(self):
        """Test creating valid message response"""
        message_id = uuid4()
        room_id = uuid4()
        sender_id = uuid4()
        now = datetime.utcnow()

        response = MessageResponse(
            id=message_id,
            room_id=room_id,
            sender_id=sender_id,
            content="Hello!",
            status="sent",
            created_at=now,
        )

        assert response.id == message_id
        assert response.room_id == room_id
        assert response.sender_id == sender_id
        assert response.content == "Hello!"
        assert response.status == "sent"
        assert response.created_at == now

    def test_different_status_values(self):
        """Test message with different status values"""
        for status in ["sent", "delivered", "read"]:
            response = MessageResponse(
                id=uuid4(),
                room_id=uuid4(),
                sender_id=uuid4(),
                content="Test",
                status=status,
                created_at=datetime.utcnow(),
            )
            assert response.status == status


class TestGetMessagesRequest:
    """Test GetMessagesRequest schema"""

    def test_create_with_all_fields(self):
        """Test creating request with all fields"""
        after_id = uuid4()
        request = GetMessagesRequest(after_message_id=after_id, limit=50)

        assert request.after_message_id == after_id
        assert request.limit == 50

    def test_create_with_defaults(self):
        """Test creating request with default values"""
        request = GetMessagesRequest()

        assert request.after_message_id is None
        assert request.limit == 50

    def test_limit_minimum_validation(self):
        """Test that limit must be at least 1"""
        with pytest.raises(ValidationError):
            GetMessagesRequest(limit=0)

    def test_limit_maximum_validation(self):
        """Test that limit cannot exceed 100"""
        with pytest.raises(ValidationError):
            GetMessagesRequest(limit=101)

    def test_limit_boundaries_valid(self):
        """Test that limit boundaries are valid"""
        # Minimum valid limit
        request1 = GetMessagesRequest(limit=1)
        assert request1.limit == 1

        # Maximum valid limit
        request2 = GetMessagesRequest(limit=100)
        assert request2.limit == 100


class TestChatRoomParticipantResponse:
    """Test ChatRoomParticipantResponse schema"""

    def test_create_with_all_fields(self):
        """Test creating participant with all fields"""
        user_id = uuid4()
        response = ChatRoomParticipantResponse(
            user_id=user_id,
            nickname="John Doe",
            avatar_url="https://example.com/avatar.jpg",
        )

        assert response.user_id == user_id
        assert response.nickname == "John Doe"
        assert response.avatar_url == "https://example.com/avatar.jpg"

    def test_create_with_minimal_fields(self):
        """Test creating participant with only required fields"""
        user_id = uuid4()
        response = ChatRoomParticipantResponse(user_id=user_id)

        assert response.user_id == user_id
        assert response.nickname is None
        assert response.avatar_url is None


class TestChatRoomResponse:
    """Test ChatRoomResponse schema"""

    def test_create_valid_response(self):
        """Test creating valid chat room response"""
        room_id = uuid4()
        participants = [
            ChatRoomParticipantResponse(
                user_id=uuid4(), nickname="User 1", avatar_url="url1"
            ),
            ChatRoomParticipantResponse(
                user_id=uuid4(), nickname="User 2", avatar_url="url2"
            ),
        ]
        now = datetime.utcnow()

        response = ChatRoomResponse(
            id=room_id,
            participants=participants,
            last_message=None,
            unread_count=0,
            created_at=now,
        )

        assert response.id == room_id
        assert len(response.participants) == 2
        assert response.unread_count == 0

    def test_with_last_message(self):
        """Test chat room with last message"""
        last_message = MessageResponse(
            id=uuid4(),
            room_id=uuid4(),
            sender_id=uuid4(),
            content="Last message",
            status="read",
            created_at=datetime.utcnow(),
        )

        response = ChatRoomResponse(
            id=uuid4(),
            participants=[],
            last_message=last_message,
            unread_count=5,
            created_at=datetime.utcnow(),
        )

        assert response.last_message is not None
        assert response.last_message.content == "Last message"
        assert response.unread_count == 5

    def test_empty_participants(self):
        """Test chat room with no participants"""
        response = ChatRoomResponse(
            id=uuid4(),
            participants=[],
            created_at=datetime.utcnow(),
        )

        assert response.participants == []


class TestMessagesListResponse:
    """Test MessagesListResponse schema"""

    def test_create_with_messages(self):
        """Test creating messages list response"""
        messages = [
            MessageResponse(
                id=uuid4(),
                room_id=uuid4(),
                sender_id=uuid4(),
                content=f"Message {i}",
                status="sent",
                created_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        response = MessagesListResponse(
            messages=messages, total=3, has_more=False
        )

        assert len(response.messages) == 3
        assert response.total == 3
        assert response.has_more is False

    def test_create_with_pagination(self):
        """Test creating response with pagination info"""
        response = MessagesListResponse(
            messages=[], total=100, has_more=True
        )

        assert response.messages == []
        assert response.total == 100
        assert response.has_more is True


class TestChatRoomListResponse:
    """Test ChatRoomListResponse schema"""

    def test_create_with_rooms(self):
        """Test creating chat room list response"""
        rooms = [
            ChatRoomResponse(
                id=uuid4(),
                participants=[],
                created_at=datetime.utcnow(),
            )
            for _ in range(2)
        ]

        response = ChatRoomListResponse(rooms=rooms, total=2)

        assert len(response.rooms) == 2
        assert response.total == 2

    def test_create_empty_list(self):
        """Test creating empty chat room list"""
        response = ChatRoomListResponse(rooms=[], total=0)

        assert response.rooms == []
        assert response.total == 0


class TestChatRoomResponseWrapper:
    """Test ChatRoomResponseWrapper schema"""

    def test_create_wrapper(self):
        """Test creating chat room response wrapper"""
        data = ChatRoomResponse(
            id=uuid4(),
            participants=[],
            created_at=datetime.utcnow(),
        )

        wrapper = ChatRoomResponseWrapper(data=data)

        assert wrapper.data == data
        assert wrapper.meta is None
        assert wrapper.error is None


class TestChatRoomListResponseWrapper:
    """Test ChatRoomListResponseWrapper schema"""

    def test_create_wrapper(self):
        """Test creating chat room list wrapper"""
        data = ChatRoomListResponse(rooms=[], total=0)
        wrapper = ChatRoomListResponseWrapper(data=data)

        assert wrapper.data == data
        assert wrapper.meta is None


class TestMessageResponseWrapper:
    """Test MessageResponseWrapper schema"""

    def test_create_wrapper(self):
        """Test creating message response wrapper"""
        data = MessageResponse(
            id=uuid4(),
            room_id=uuid4(),
            sender_id=uuid4(),
            content="Test",
            status="sent",
            created_at=datetime.utcnow(),
        )

        wrapper = MessageResponseWrapper(data=data)

        assert wrapper.data == data
        assert wrapper.meta is None


class TestMessagesListResponseWrapper:
    """Test MessagesListResponseWrapper schema"""

    def test_create_wrapper(self):
        """Test creating messages list wrapper"""
        data = MessagesListResponse(
            messages=[], total=0, has_more=False
        )

        wrapper = MessagesListResponseWrapper(data=data)

        assert wrapper.data == data
        assert wrapper.meta is None


class TestSchemaExamples:
    """Test that schema examples are valid"""

    def test_send_message_request_example(self):
        """Test that SendMessageRequest example is valid"""
        example = {"content": "Hello! I'm interested in trading cards."}

        request = SendMessageRequest(**example)
        assert request.content == "Hello! I'm interested in trading cards."

    def test_get_messages_request_example(self):
        """Test that GetMessagesRequest example is valid"""
        example = {
            "after_message_id": "123e4567-e89b-12d3-a456-426614174000",
            "limit": 50,
        }

        request = GetMessagesRequest(**example)
        assert request.limit == 50
