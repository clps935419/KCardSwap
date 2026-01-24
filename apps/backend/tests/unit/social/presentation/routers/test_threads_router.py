"""
Unit tests for Threads Router

Tests the threads router endpoints with mocked use cases.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modules.social.domain.entities.thread import MessageThread
from app.modules.social.domain.entities.thread_message import ThreadMessage
from app.modules.social.presentation.routers.threads_router import (
    get_my_threads,
    get_thread_messages,
    send_message,
)
from app.modules.social.presentation.schemas.message_schemas import (
    SendMessageRequest,
)


class TestThreadsRouter:
    """Test Threads Router endpoints"""

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_other_user_id(self):
        """Create sample other user ID"""
        return uuid4()

    @pytest.fixture
    def sample_thread_id(self):
        """Create sample thread ID"""
        return str(uuid4())

    @pytest.fixture
    def sample_message_id(self):
        """Create sample message ID"""
        return str(uuid4())

    @pytest.fixture
    def sample_post_id(self):
        """Create sample post ID"""
        return str(uuid4())

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        return AsyncMock()

    @pytest.fixture
    def sample_thread(self, sample_thread_id, sample_user_id, sample_other_user_id):
        """Create sample thread"""
        return MessageThread(
            id=sample_thread_id,
            user_a_id=str(sample_user_id),
            user_b_id=str(sample_other_user_id),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_message_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_thread_message(self, sample_message_id, sample_thread_id, sample_user_id):
        """Create sample thread message"""
        return ThreadMessage(
            id=sample_message_id,
            thread_id=sample_thread_id,
            sender_id=str(sample_user_id),
            content="Hello!",
            post_id=None,
            created_at=datetime.now(timezone.utc),
        )

    # Tests for GET /threads
    @pytest.mark.asyncio
    async def test_get_my_threads_success(
        self, sample_user_id, mock_session, sample_thread
    ):
        """Test successful retrieval of user's threads"""
        # Arrange
        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.GetThreadsUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.return_value = [sample_thread]
                mock_use_case_class.return_value = mock_use_case
                
                # Act
                response = await get_my_threads(
                    limit=50,
                    offset=0,
                    user_id=sample_user_id,
                    session=mock_session,
                )

        # Assert
        assert response.total == 1
        assert len(response.threads) == 1
        assert response.threads[0].id == sample_thread.id

    @pytest.mark.asyncio
    async def test_get_my_threads_empty(
        self, sample_user_id, mock_session
    ):
        """Test retrieval of threads when none exist"""
        # Arrange
        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.GetThreadsUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.return_value = []
                mock_use_case_class.return_value = mock_use_case
                
                # Act
                response = await get_my_threads(
                    limit=50,
                    offset=0,
                    user_id=sample_user_id,
                    session=mock_session,
                )

        # Assert
        assert response.total == 0
        assert len(response.threads) == 0

    @pytest.mark.asyncio
    async def test_get_my_threads_with_pagination(
        self, sample_user_id, mock_session, sample_thread
    ):
        """Test retrieval of threads with pagination"""
        # Arrange
        threads = [sample_thread]
        
        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.GetThreadsUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.return_value = threads
                mock_use_case_class.return_value = mock_use_case
                
                # Act
                response = await get_my_threads(
                    limit=10,
                    offset=5,
                    user_id=sample_user_id,
                    session=mock_session,
                )

        # Assert
        assert len(response.threads) == 1
        mock_use_case.execute.assert_called_once_with(
            user_id=str(sample_user_id), limit=10, offset=5
        )

    @pytest.mark.asyncio
    async def test_get_my_threads_multiple(
        self, sample_user_id, sample_other_user_id, mock_session
    ):
        """Test retrieval of multiple threads"""
        # Arrange
        thread1 = MessageThread(
            id=str(uuid4()),
            user_a_id=str(sample_user_id),
            user_b_id=str(sample_other_user_id),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_message_at=datetime.now(timezone.utc),
        )
        thread2 = MessageThread(
            id=str(uuid4()),
            user_a_id=str(sample_user_id),
            user_b_id=str(uuid4()),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_message_at=datetime.now(timezone.utc),
        )
        
        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.GetThreadsUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.return_value = [thread1, thread2]
                mock_use_case_class.return_value = mock_use_case
                
                # Act
                response = await get_my_threads(
                    limit=50,
                    offset=0,
                    user_id=sample_user_id,
                    session=mock_session,
                )

        # Assert
        assert response.total == 2

    # Tests for GET /threads/{thread_id}/messages
    @pytest.mark.asyncio
    async def test_get_thread_messages_success(
        self, sample_user_id, sample_thread_id, mock_session, sample_thread_message
    ):
        """Test successful retrieval of thread messages"""
        # Arrange
        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.GetThreadMessagesUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.return_value = [sample_thread_message]
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act
                    response = await get_thread_messages(
                        thread_id=sample_thread_id,
                        limit=50,
                        offset=0,
                        user_id=sample_user_id,
                        session=mock_session,
                    )

        # Assert
        assert response.total == 1
        assert len(response.messages) == 1
        assert response.messages[0].content == "Hello!"

    @pytest.mark.asyncio
    async def test_get_thread_messages_empty(
        self, sample_user_id, sample_thread_id, mock_session
    ):
        """Test retrieval of messages when thread is empty"""
        # Arrange
        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.GetThreadMessagesUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.return_value = []
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act
                    response = await get_thread_messages(
                        thread_id=sample_thread_id,
                        limit=50,
                        offset=0,
                        user_id=sample_user_id,
                        session=mock_session,
                    )

        # Assert
        assert response.total == 0

    @pytest.mark.asyncio
    async def test_get_thread_messages_not_participant(
        self, sample_user_id, sample_thread_id, mock_session
    ):
        """Test retrieval of messages by non-participant"""
        # Arrange
        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.GetThreadMessagesUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.side_effect = ValueError("User not part of thread")
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act & Assert
                    with pytest.raises(HTTPException) as exc_info:
                        await get_thread_messages(
                            thread_id=sample_thread_id,
                            limit=50,
                            offset=0,
                            user_id=sample_user_id,
                            session=mock_session,
                        )
                    assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_thread_messages_with_pagination(
        self, sample_user_id, sample_thread_id, mock_session, sample_thread_message
    ):
        """Test retrieval of messages with pagination"""
        # Arrange
        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.GetThreadMessagesUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.return_value = [sample_thread_message]
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act
                    response = await get_thread_messages(
                        thread_id=sample_thread_id,
                        limit=20,
                        offset=10,
                        user_id=sample_user_id,
                        session=mock_session,
                    )

        # Assert
        mock_use_case.execute.assert_called_once_with(
            thread_id=sample_thread_id,
            user_id=str(sample_user_id),
            limit=20,
            offset=10,
        )

    # Tests for POST /threads/{thread_id}/messages
    @pytest.mark.asyncio
    async def test_send_message_success(
        self, sample_user_id, sample_thread_id, mock_session, sample_thread_message
    ):
        """Test successful message sending"""
        # Arrange
        request = SendMessageRequest(content="Hello!")

        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.SendMessageUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.return_value = sample_thread_message
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act
                    response = await send_message(
                        thread_id=sample_thread_id,
                        request=request,
                        user_id=sample_user_id,
                        session=mock_session,
                    )

        # Assert
        assert response.content == "Hello!"
        assert response.thread_id == sample_thread_id

    @pytest.mark.asyncio
    async def test_send_message_with_post_reference(
        self, sample_user_id, sample_thread_id, sample_post_id, mock_session
    ):
        """Test sending message with post reference"""
        # Arrange
        request = SendMessageRequest(content="Check out this post!", post_id=sample_post_id)

        message = ThreadMessage(
            id=str(uuid4()),
            thread_id=sample_thread_id,
            sender_id=str(sample_user_id),
            content=request.content,
            post_id=sample_post_id,
            created_at=datetime.now(timezone.utc),
        )

        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.SendMessageUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.return_value = message
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act
                    response = await send_message(
                        thread_id=sample_thread_id,
                        request=request,
                        user_id=sample_user_id,
                        session=mock_session,
                    )

        # Assert
        assert response.post_id == sample_post_id

    @pytest.mark.asyncio
    async def test_send_message_not_participant(
        self, sample_user_id, sample_thread_id, mock_session
    ):
        """Test sending message by non-participant"""
        # Arrange
        request = SendMessageRequest(content="Hello!")

        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.SendMessageUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.side_effect = ValueError("User not part of thread")
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act & Assert
                    with pytest.raises(HTTPException) as exc_info:
                        await send_message(
                            thread_id=sample_thread_id,
                            request=request,
                            user_id=sample_user_id,
                            session=mock_session,
                        )
                    assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_send_message_empty_content(
        self, sample_user_id, sample_thread_id, mock_session
    ):
        """Test sending message with empty content"""
        # Arrange
        request = SendMessageRequest(content="a")  # Valid content for schema validation

        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.SendMessageUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.side_effect = ValueError("Content cannot be empty")
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act & Assert
                    with pytest.raises(HTTPException) as exc_info:
                        await send_message(
                            thread_id=sample_thread_id,
                            request=request,
                            user_id=sample_user_id,
                            session=mock_session,
                        )
                    assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_send_message_thread_not_found(
        self, sample_user_id, sample_thread_id, mock_session
    ):
        """Test sending message to non-existent thread"""
        # Arrange
        request = SendMessageRequest(content="Hello!")

        with patch("app.modules.social.presentation.routers.threads_router.ThreadRepository"):
            with patch("app.modules.social.presentation.routers.threads_router.ThreadMessageRepository"):
                with patch("app.modules.social.presentation.routers.threads_router.SendMessageUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.side_effect = ValueError("Thread not found")
                    mock_use_case_class.return_value = mock_use_case
                    
                    # Act & Assert
                    with pytest.raises(HTTPException) as exc_info:
                        await send_message(
                            thread_id=sample_thread_id,
                            request=request,
                            user_id=sample_user_id,
                            session=mock_session,
                        )
                    assert exc_info.value.status_code == 403
