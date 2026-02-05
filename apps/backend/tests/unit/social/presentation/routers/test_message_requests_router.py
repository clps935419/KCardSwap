"""
Unit tests for Message Requests Router

Tests the message requests router endpoints with mocked use cases.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modules.social.domain.entities.message_request import (
    MessageRequest,
    RequestStatus,
)
from app.modules.social.domain.entities.thread import MessageThread
from app.modules.social.presentation.routers.message_requests_router import (
    accept_message_request,
    create_message_request,
    decline_message_request,
    get_my_message_requests,
)
from app.modules.social.presentation.schemas.message_schemas import (
    CreateMessageRequestRequest,
)


class TestMessageRequestsRouter:
    """Test Message Requests Router endpoints"""

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_recipient_id(self):
        """Create sample recipient ID"""
        return uuid4()

    @pytest.fixture
    def sample_request_id(self):
        """Create sample request ID"""
        return str(uuid4())

    @pytest.fixture
    def sample_thread_id(self):
        """Create sample thread ID"""
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
    def sample_message_request(self, sample_request_id, sample_user_id, sample_recipient_id):
        """Create sample message request"""
        return MessageRequest(
            id=sample_request_id,
            sender_id=str(sample_user_id),
            recipient_id=str(sample_recipient_id),
            initial_message="Hello!",
            post_id=None,
            status=RequestStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_thread(self, sample_thread_id, sample_user_id, sample_recipient_id):
        """Create sample thread"""
        return MessageThread(
            id=sample_thread_id,
            user_a_id=str(sample_user_id),
            user_b_id=str(sample_recipient_id),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    # Tests for POST /message-requests
    @pytest.mark.asyncio
    async def test_create_message_request_success(
        self, sample_user_id, sample_recipient_id, mock_session, sample_message_request
    ):
        """Test successful message request creation"""
        # Arrange
        request = CreateMessageRequestRequest(
            recipient_id=str(sample_recipient_id),
            initial_message="Hello!",
        )

        with MagicMock():
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = sample_message_request

            with MagicMock():
                mock_profile = MagicMock()
                mock_profile.privacy_flags = {"allow_stranger_chat": True}

                from unittest.mock import patch
                with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
                    with patch("app.modules.social.presentation.routers.message_requests_router.ThreadRepository"):
                        with patch("app.modules.social.presentation.routers.message_requests_router.FriendshipRepositoryImpl"):
                            with patch("app.modules.social.presentation.routers.message_requests_router.ProfileRepositoryImpl") as mock_profile_repo_class:
                                with patch("app.modules.social.presentation.routers.message_requests_router.ThreadUniquenessService"):
                                    with patch("app.modules.social.presentation.routers.message_requests_router.CreateMessageRequestUseCase") as mock_use_case_class:
                                        mock_profile_repo_inst = AsyncMock()
                                        mock_profile_repo_inst.get_by_user_id.return_value = mock_profile
                                        mock_profile_repo_class.return_value = mock_profile_repo_inst

                                        mock_use_case_class.return_value = mock_use_case

                                        # Act
                                        response = await create_message_request(
                                            request=request,
                                            user_id=sample_user_id,
                                            session=mock_session,
                                        )

        # Assert
        assert response.sender_id == str(sample_user_id)
        assert response.recipient_id == str(sample_recipient_id)
        assert response.initial_message == "Hello!"
        assert response.status == "pending"

    @pytest.mark.asyncio
    async def test_create_message_request_with_post(
        self, sample_user_id, sample_recipient_id, sample_post_id, mock_session
    ):
        """Test message request creation with post reference"""
        # Arrange
        request = CreateMessageRequestRequest(
            recipient_id=str(sample_recipient_id),
            initial_message="Interested in this post!",
            post_id=sample_post_id,
        )

        message_request = MessageRequest(
            id=str(uuid4()),
            sender_id=str(sample_user_id),
            recipient_id=str(sample_recipient_id),
            initial_message=request.initial_message,
            post_id=sample_post_id,
            status=RequestStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.ThreadRepository"):
                with patch("app.modules.social.presentation.routers.message_requests_router.FriendshipRepositoryImpl"):
                    with patch("app.modules.social.presentation.routers.message_requests_router.ProfileRepositoryImpl") as mock_profile_repo_class:
                        with patch("app.modules.social.presentation.routers.message_requests_router.ThreadUniquenessService"):
                            with patch("app.modules.social.presentation.routers.message_requests_router.CreateMessageRequestUseCase") as mock_use_case_class:
                                mock_profile_repo_inst = AsyncMock()
                                mock_profile = MagicMock()
                                mock_profile.privacy_flags = {"allow_stranger_chat": True}
                                mock_profile_repo_inst.get_by_user_id.return_value = mock_profile
                                mock_profile_repo_class.return_value = mock_profile_repo_inst

                                mock_use_case = AsyncMock()
                                mock_use_case.execute.return_value = message_request
                                mock_use_case_class.return_value = mock_use_case

                                # Act
                                response = await create_message_request(
                                    request=request,
                                    user_id=sample_user_id,
                                    session=mock_session,
                                )

        # Assert
        assert response.post_id == sample_post_id

    @pytest.mark.asyncio
    async def test_create_message_request_blocked_by_privacy(
        self, sample_user_id, sample_recipient_id, mock_session
    ):
        """Test message request creation blocked by privacy settings"""
        # Arrange
        request = CreateMessageRequestRequest(
            recipient_id=str(sample_recipient_id),
            initial_message="Hello!",
        )

        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.ThreadRepository"):
                with patch("app.modules.social.presentation.routers.message_requests_router.FriendshipRepositoryImpl"):
                    with patch("app.modules.social.presentation.routers.message_requests_router.ProfileRepositoryImpl") as mock_profile_repo_class:
                        with patch("app.modules.social.presentation.routers.message_requests_router.ThreadUniquenessService"):
                            with patch("app.modules.social.presentation.routers.message_requests_router.CreateMessageRequestUseCase") as mock_use_case_class:
                                mock_profile_repo_inst = AsyncMock()
                                mock_profile = MagicMock()
                                mock_profile.privacy_flags = {"allow_stranger_chat": False}
                                mock_profile_repo_inst.get_by_user_id.return_value = mock_profile
                                mock_profile_repo_class.return_value = mock_profile_repo_inst

                                mock_use_case = AsyncMock()
                                mock_use_case.execute.side_effect = ValueError(
                                    "Recipient does not allow stranger messages"
                                )
                                mock_use_case_class.return_value = mock_use_case

                                # Act & Assert
                                with pytest.raises(HTTPException) as exc_info:
                                    await create_message_request(
                                        request=request,
                                        user_id=sample_user_id,
                                        session=mock_session,
                                    )
                                assert exc_info.value.status_code == 400

    # Tests for GET /message-requests/inbox
    @pytest.mark.asyncio
    async def test_get_my_message_requests_success(
        self, sample_user_id, mock_session, sample_message_request
    ):
        """Test successful retrieval of message requests"""
        # Arrange
        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.GetMessageRequestsUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.return_value = [sample_message_request]
                mock_use_case_class.return_value = mock_use_case

                # Act
                response = await get_my_message_requests(
                    status_filter="pending",
                    user_id=sample_user_id,
                    session=mock_session,
                )

        # Assert
        assert len(response) == 1
        assert response[0].status == "pending"

    @pytest.mark.asyncio
    async def test_get_my_message_requests_all_statuses(
        self, sample_user_id, mock_session
    ):
        """Test retrieval of message requests with 'all' filter"""
        # Arrange
        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.GetMessageRequestsUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.return_value = []
                mock_use_case_class.return_value = mock_use_case

                # Act
                response = await get_my_message_requests(
                    status_filter="all",
                    user_id=sample_user_id,
                    session=mock_session,
                )

        # Assert
        assert len(response) == 0

    # Tests for POST /message-requests/{request_id}/accept
    @pytest.mark.asyncio
    async def test_accept_message_request_success(
        self, sample_user_id, sample_request_id, mock_session, sample_message_request, sample_thread
    ):
        """Test successful message request acceptance"""
        # Arrange
        sample_message_request.status = RequestStatus.ACCEPTED
        sample_message_request.thread_id = sample_thread.id

        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.ThreadRepository"):
                with patch("app.modules.social.presentation.routers.message_requests_router.AcceptMessageRequestUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.return_value = (sample_message_request, sample_thread)
                    mock_use_case_class.return_value = mock_use_case

                    # Act
                    response = await accept_message_request(
                        request_id=sample_request_id,
                        user_id=sample_user_id,
                        session=mock_session,
                    )

        # Assert
        assert response.message_request.status == "accepted"
        assert response.thread.id == sample_thread.id

    @pytest.mark.asyncio
    async def test_accept_message_request_not_found(
        self, sample_user_id, sample_request_id, mock_session
    ):
        """Test acceptance of non-existent message request"""
        # Arrange
        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.ThreadRepository"):
                with patch("app.modules.social.presentation.routers.message_requests_router.AcceptMessageRequestUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.side_effect = ValueError("Request not found")
                    mock_use_case_class.return_value = mock_use_case

                    # Act & Assert
                    with pytest.raises(HTTPException) as exc_info:
                        await accept_message_request(
                            request_id=sample_request_id,
                            user_id=sample_user_id,
                            session=mock_session,
                        )
                    assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_accept_message_request_not_recipient(
        self, sample_user_id, sample_request_id, mock_session
    ):
        """Test acceptance of message request by non-recipient"""
        # Arrange
        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.ThreadRepository"):
                with patch("app.modules.social.presentation.routers.message_requests_router.AcceptMessageRequestUseCase") as mock_use_case_class:
                    mock_use_case = AsyncMock()
                    mock_use_case.execute.side_effect = ValueError("Not the recipient")
                    mock_use_case_class.return_value = mock_use_case

                    # Act & Assert
                    with pytest.raises(HTTPException) as exc_info:
                        await accept_message_request(
                            request_id=sample_request_id,
                            user_id=sample_user_id,
                            session=mock_session,
                        )
                    assert exc_info.value.status_code == 400

    # Tests for POST /message-requests/{request_id}/decline
    @pytest.mark.asyncio
    async def test_decline_message_request_success(
        self, sample_user_id, sample_request_id, mock_session, sample_message_request
    ):
        """Test successful message request decline"""
        # Arrange
        sample_message_request.status = RequestStatus.DECLINED

        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.DeclineMessageRequestUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.return_value = sample_message_request
                mock_use_case_class.return_value = mock_use_case

                # Act
                response = await decline_message_request(
                    request_id=sample_request_id,
                    user_id=sample_user_id,
                    session=mock_session,
                )

        # Assert
        assert response.status == "declined"

    @pytest.mark.asyncio
    async def test_decline_message_request_not_found(
        self, sample_user_id, sample_request_id, mock_session
    ):
        """Test decline of non-existent message request"""
        # Arrange
        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.DeclineMessageRequestUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.side_effect = ValueError("Request not found")
                mock_use_case_class.return_value = mock_use_case

                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    await decline_message_request(
                        request_id=sample_request_id,
                        user_id=sample_user_id,
                        session=mock_session,
                    )
                assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_decline_message_request_not_recipient(
        self, sample_user_id, sample_request_id, mock_session
    ):
        """Test decline of message request by non-recipient"""
        # Arrange
        from unittest.mock import patch
        with patch("app.modules.social.presentation.routers.message_requests_router.MessageRequestRepository"):
            with patch("app.modules.social.presentation.routers.message_requests_router.DeclineMessageRequestUseCase") as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case.execute.side_effect = ValueError("Not the recipient")
                mock_use_case_class.return_value = mock_use_case

                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    await decline_message_request(
                        request_id=sample_request_id,
                        user_id=sample_user_id,
                        session=mock_session,
                    )
                assert exc_info.value.status_code == 400
