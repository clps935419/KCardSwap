"""
Unit tests for CardRepositoryImpl

Tests the card repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.card import Card
from app.modules.social.infrastructure.database.models.card_model import CardModel
from app.modules.social.infrastructure.repositories.card_repository_impl import (
    CardRepositoryImpl,
)


class TestCardRepositoryImpl:
    """Test CardRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return CardRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_card(self):
        """Create sample Card entity"""
        return Card(
            id=uuid4(),
            owner_id=uuid4(),
            idol="IU",
            idol_group="Solo",
            album="Love Poem",
            image_url="https://example.com/image.jpg",
            status="available",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_card_model(self, sample_card):
        """Create sample CardModel"""
        return CardModel(
            id=sample_card.id,
            owner_id=sample_card.owner_id,
            idol=sample_card.idol,
            idol_group=sample_card.idol_group,
            album=sample_card.album,
            image_url=sample_card.image_url,
            status=sample_card.status,
            upload_status=sample_card.upload_status,
            created_at=sample_card.created_at,
            updated_at=sample_card.updated_at,
        )

    @pytest.mark.asyncio
    async def test_save_card(self, repository, mock_session, sample_card):
        """Test saving a card"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No existing card
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.save(sample_card)

        # Assert
        assert result is not None
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_id_found(self, repository, mock_session, sample_card_model):
        """Test finding card by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_card_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_id(sample_card_model.id)

        # Assert
        assert result is not None
        assert result.id == sample_card_model.id

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository, mock_session):
        """Test finding card by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_id(uuid4())

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_owner(self, repository, mock_session):
        """Test finding cards by owner"""
        # Arrange
        owner_id = uuid4()
        card_models = [
            CardModel(
                id=uuid4(),
                owner_id=owner_id,
                idol=f"Idol {i}",
                idol_group="Group",
                album=f"Album {i}",
                image_url=f"https://example.com/image{i}.jpg",
                status="available",
                upload_status="confirmed",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = card_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_owner(owner_id)

        # Assert
        assert len(result) == 3
        for card in result:
            assert card.owner_id == owner_id

    @pytest.mark.asyncio
    async def test_delete_card_success(self, repository, mock_session, sample_card_model):
        """Test deleting a card that exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_card_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.delete(sample_card_model.id)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_card_not_found(self, repository, mock_session):
        """Test deleting a card that doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.delete(uuid4())

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_count_uploads_today(self, repository, mock_session):
        """Test counting uploads for today"""
        # Arrange
        owner_id = uuid4()
        expected_count = 5

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.count_uploads_today(owner_id)

        # Assert
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_get_total_storage_used(self, repository, mock_session):
        """Test getting total storage used"""
        # Arrange
        owner_id = uuid4()
        expected_bytes = 1024000

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_bytes
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_total_storage_used(owner_id)

        # Assert
        assert result == expected_bytes

    @pytest.mark.asyncio
    async def test_find_by_status(self, repository, mock_session):
        """Test finding cards by status"""
        # Arrange
        owner_id = uuid4()
        status = "available"

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_status(owner_id, status)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_nearby_cards(self, repository, mock_session):
        """Test finding nearby cards"""
        # Arrange
        lat = 25.033
        lng = 121.564
        radius_km = 5.0
        exclude_user_id = uuid4()

        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_nearby_cards(
            lat, lng, radius_km, exclude_user_id
        )

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()
