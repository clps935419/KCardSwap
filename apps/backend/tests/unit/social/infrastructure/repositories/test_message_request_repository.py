"""
Unit tests for MessageRequestRepository

Tests the message request repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.message_request import (
    MessageRequest,
    RequestStatus,
)
from app.modules.social.infrastructure.database.models.message_request_model import (
    MessageRequestModel,
)
from app.modules.social.infrastructure.repositories.message_request_repository import (
    MessageRequestRepository,
)


class TestMessageRequestRepository:
    """Test MessageRequestRepository"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return MessageRequestRepository(mock_session)

    @pytest.fixture
    def sample_message_request(self):
        """Create sample MessageRequest entity"""
        return MessageRequest(
            id=str(uuid4()),
            sender_id=str(uuid4()),
            recipient_id=str(uuid4()),
            initial_message="Hi, interested in your card!",
            post_id=str(uuid4()),
            status=RequestStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            thread_id=None,
        )

    @pytest.fixture
    def sample_request_model(self, sample_message_request):
        """Create sample MessageRequestModel"""
        return MessageRequestModel(
            id=UUID(sample_message_request.id),
            sender_id=UUID(sample_message_request.sender_id),
            recipient_id=UUID(sample_message_request.recipient_id),
            initial_message=sample_message_request.initial_message,
            post_id=UUID(sample_message_request.post_id) if sample_message_request.post_id else None,
            status=sample_message_request.status.value,
            thread_id=UUID(sample_message_request.thread_id) if sample_message_request.thread_id else None,
            created_at=sample_message_request.created_at,
            updated_at=sample_message_request.updated_at,
        )

    @pytest.mark.asyncio
    async def test_create_message_request(
        self, repository, mock_session, sample_message_request
    ):
        """Test creating a new message request"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_message_request)

        # Assert
        assert result is not None
        assert result.id == sample_message_request.id
        assert result.sender_id == sample_message_request.sender_id
        assert result.recipient_id == sample_message_request.recipient_id
        assert result.status == RequestStatus.PENDING
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repository, mock_session, sample_request_model
    ):
        """Test getting message request by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_request_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(sample_request_model.id))

        # Assert
        assert result is not None
        assert result.id == str(sample_request_model.id)
        assert result.initial_message == sample_request_model.initial_message

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting message request by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(str(uuid4()))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_find_pending_between_users_found(
        self, repository, mock_session, sample_request_model
    ):
        """Test finding pending request between users when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_request_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_pending_between_users(
            str(sample_request_model.sender_id),
            str(sample_request_model.recipient_id),
        )

        # Assert
        assert result is not None
        assert result.status == RequestStatus.PENDING

    @pytest.mark.asyncio
    async def test_find_pending_between_users_not_found(
        self, repository, mock_session
    ):
        """Test finding pending request when none exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_pending_between_users(
            str(uuid4()), str(uuid4())
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_requests_for_recipient_all(self, repository, mock_session):
        """Test getting all requests for a recipient"""
        # Arrange
        recipient_id = str(uuid4())
        request_models = [
            MessageRequestModel(
                id=uuid4(),
                sender_id=uuid4(),
                recipient_id=UUID(recipient_id),
                initial_message=f"Message {i}",
                post_id=uuid4(),
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = request_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_requests_for_recipient(recipient_id)

        # Assert
        assert len(result) == 3
        for req in result:
            assert req.recipient_id == recipient_id

    @pytest.mark.asyncio
    async def test_get_requests_for_recipient_filtered_by_status(
        self, repository, mock_session
    ):
        """Test getting requests filtered by status"""
        # Arrange
        recipient_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_requests_for_recipient(
            recipient_id, status=RequestStatus.ACCEPTED
        )

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_message_request(
        self, repository, mock_session, sample_message_request, sample_request_model
    ):
        """Test updating an existing message request"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_request_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create updated request
        updated_request = MessageRequest(
            id=sample_message_request.id,
            sender_id=sample_message_request.sender_id,
            recipient_id=sample_message_request.recipient_id,
            initial_message=sample_message_request.initial_message,
            post_id=sample_message_request.post_id,
            status=RequestStatus.ACCEPTED,
            thread_id=str(uuid4()),
            created_at=sample_message_request.created_at,
            updated_at=datetime.utcnow(),
        )

        # Act
        result = await repository.update(updated_request)

        # Assert
        assert result is not None
        assert result.id == updated_request.id
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_message_request(
        self, repository, mock_session, sample_request_model
    ):
        """Test deleting a message request"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = sample_request_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        await repository.delete(str(sample_request_model.id))

        # Assert
        mock_session.delete.assert_called_once()
        mock_session.flush.assert_called_once()
