"""
Unit tests for SubscriptionRepositoryImpl

Tests the subscription repository implementation with mocked database session.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain.entities.subscription import Subscription
from app.modules.identity.infrastructure.database.models.subscription_model import (
    SubscriptionModel,
)
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import (
    SubscriptionRepositoryImpl,
)


class TestSubscriptionRepositoryImpl:
    """Test SubscriptionRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return SubscriptionRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_subscription(self):
        """Create sample Subscription entity"""
        return Subscription(
            id=uuid4(),
            user_id=uuid4(),
            plan="premium",
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=30),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_subscription_model(self, sample_subscription):
        """Create sample SubscriptionModel"""
        return SubscriptionModel(
            id=sample_subscription.id,
            user_id=sample_subscription.user_id,
            plan=sample_subscription.plan,
            status=sample_subscription.status,
            expires_at=sample_subscription.expires_at,
            created_at=sample_subscription.created_at,
            updated_at=sample_subscription.updated_at,
        )

    @pytest.mark.asyncio
    async def test_create_subscription(
        self, repository, mock_session, sample_subscription
    ):
        """Test creating a new subscription"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_subscription)

        # Assert
        assert result is not None
        assert result.id == sample_subscription.id
        assert result.user_id == sample_subscription.user_id
        assert result.plan == sample_subscription.plan
        assert result.status == sample_subscription.status
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repository, mock_session, sample_subscription_model
    ):
        """Test getting subscription by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_subscription_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(sample_subscription_model.id)

        # Assert
        assert result is not None
        assert result.id == sample_subscription_model.id
        assert result.plan == sample_subscription_model.plan
        assert result.status == sample_subscription_model.status

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting subscription by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_id(uuid4())

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id_found(
        self, repository, mock_session, sample_subscription_model
    ):
        """Test getting subscription by user ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_subscription_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_user_id(sample_subscription_model.user_id)

        # Assert
        assert result is not None
        assert result.user_id == sample_subscription_model.user_id

    @pytest.mark.asyncio
    async def test_get_by_user_id_not_found(self, repository, mock_session):
        """Test getting subscription by user ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_user_id(uuid4())

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_subscription(
        self, repository, mock_session, sample_subscription, sample_subscription_model
    ):
        """Test updating an existing subscription"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_subscription_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create modified subscription
        updated_subscription = Subscription(
            id=sample_subscription.id,
            user_id=sample_subscription.user_id,
            plan="free",
            status="expired",
            expires_at=sample_subscription.expires_at,
            created_at=sample_subscription.created_at,
            updated_at=datetime.utcnow(),
        )

        # Act
        result = await repository.update(updated_subscription)

        # Assert
        assert result is not None
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_non_existing_subscription(
        self, repository, mock_session, sample_subscription
    ):
        """Test updating a non-existing subscription raises error"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(ValueError, match="Subscription with id .* not found"):
            await repository.update(sample_subscription)

    @pytest.mark.asyncio
    async def test_get_expired_subscriptions(self, repository, mock_session):
        """Test getting expired subscriptions"""
        # Arrange
        before_time = datetime.utcnow()
        expired_models = [
            SubscriptionModel(
                id=uuid4(),
                user_id=uuid4(),
                plan="premium",
                status="active",
                expires_at=datetime.utcnow() - timedelta(days=i),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for i in range(1, 4)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = expired_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_expired_subscriptions(before_time)

        # Assert
        assert len(result) == 3
        for subscription in result:
            assert subscription.status == "active"
            assert subscription.expires_at <= before_time

    @pytest.mark.asyncio
    async def test_get_or_create_by_user_id_existing(
        self, repository, mock_session, sample_subscription_model
    ):
        """Test get_or_create when subscription exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_subscription_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_or_create_by_user_id(
            sample_subscription_model.user_id
        )

        # Assert
        assert result is not None
        assert result.user_id == sample_subscription_model.user_id
        assert result.plan == sample_subscription_model.plan

    @pytest.mark.asyncio
    async def test_get_or_create_by_user_id_new(self, repository, mock_session):
        """Test get_or_create when subscription doesn't exist"""
        # Arrange
        user_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.get_or_create_by_user_id(user_id)

        # Assert
        assert result is not None
        assert result.user_id == user_id
        assert result.plan == "free"
        assert result.status == "inactive"
        assert result.expires_at is None
        mock_session.add.assert_called_once()
