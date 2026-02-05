"""
Unit tests for GalleryCardRepository

Tests the gallery card repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.gallery_card import GalleryCard
from app.modules.social.infrastructure.models.gallery_card_model import GalleryCardModel
from app.modules.social.infrastructure.repositories.gallery_card_repository import (
    GalleryCardRepository,
)


class TestGalleryCardRepository:
    """Test GalleryCardRepository"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return GalleryCardRepository(mock_session)

    @pytest.fixture
    def sample_gallery_card(self):
        """Create sample GalleryCard entity"""
        return GalleryCard(
            id=uuid4(),
            user_id=uuid4(),
            title="IU Love Poem Card",
            idol_name="IU",
            era="Love Poem",
            description="Limited edition photocard",
            media_asset_id=uuid4(),
            display_order=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_gallery_card_model(self, sample_gallery_card):
        """Create sample GalleryCardModel"""
        return GalleryCardModel(
            id=sample_gallery_card.id,
            user_id=sample_gallery_card.user_id,
            title=sample_gallery_card.title,
            idol_name=sample_gallery_card.idol_name,
            era=sample_gallery_card.era,
            description=sample_gallery_card.description,
            media_asset_id=sample_gallery_card.media_asset_id,
            display_order=sample_gallery_card.display_order,
            created_at=sample_gallery_card.created_at,
            updated_at=sample_gallery_card.updated_at,
        )

    @pytest.mark.asyncio
    async def test_create_gallery_card(
        self, repository, mock_session, sample_gallery_card
    ):
        """Test creating a new gallery card"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_gallery_card)

        # Assert
        assert result is not None
        assert result.id == sample_gallery_card.id
        assert result.title == sample_gallery_card.title
        assert result.idol_name == sample_gallery_card.idol_name
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_id_found(
        self, repository, mock_session, sample_gallery_card_model
    ):
        """Test finding gallery card by ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_gallery_card_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_id(sample_gallery_card_model.id)

        # Assert
        assert result is not None
        assert result.id == sample_gallery_card_model.id
        assert result.title == sample_gallery_card_model.title

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository, mock_session):
        """Test finding gallery card by ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_id(uuid4())

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_user_id(self, repository, mock_session):
        """Test finding all gallery cards for a user"""
        # Arrange
        user_id = uuid4()
        card_models = [
            GalleryCardModel(
                id=uuid4(),
                user_id=user_id,
                title=f"Card {i}",
                idol_name="IU",
                era="Love Poem",
                description="Description",
                media_asset_id=uuid4(),
                display_order=i,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = card_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_user_id(user_id)

        # Assert
        assert len(result) == 3
        for card in result:
            assert card.user_id == user_id

    @pytest.mark.asyncio
    async def test_find_by_user_id_with_pagination(self, repository, mock_session):
        """Test finding gallery cards with limit and offset"""
        # Arrange
        user_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_user_id(user_id, limit=10, offset=5)

        # Assert
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_gallery_card(
        self, repository, mock_session, sample_gallery_card, sample_gallery_card_model
    ):
        """Test updating an existing gallery card"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_gallery_card_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create updated card
        updated_card = GalleryCard(
            id=sample_gallery_card.id,
            user_id=sample_gallery_card.user_id,
            title="Updated Title",
            idol_name=sample_gallery_card.idol_name,
            era=sample_gallery_card.era,
            description="Updated description",
            media_asset_id=sample_gallery_card.media_asset_id,
            display_order=2,
            created_at=sample_gallery_card.created_at,
            updated_at=datetime.utcnow(),
        )

        # Act
        result = await repository.update(updated_card)

        # Assert
        assert result is not None
        assert result.id == updated_card.id
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_non_existing_card(
        self, repository, mock_session, sample_gallery_card
    ):
        """Test updating a non-existing gallery card raises error"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(ValueError, match="GalleryCard with id .* not found"):
            await repository.update(sample_gallery_card)

    @pytest.mark.asyncio
    async def test_delete_existing_card(
        self, repository, mock_session, sample_gallery_card_model
    ):
        """Test deleting an existing gallery card"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_gallery_card_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.delete(sample_gallery_card_model.id)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_non_existing_card(self, repository, mock_session):
        """Test deleting a non-existing gallery card"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.delete(uuid4())

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_count_by_user_id(self, repository, mock_session):
        """Test counting gallery cards for a user"""
        # Arrange
        user_id = uuid4()
        expected_count = 5

        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.count_by_user_id(user_id)

        # Assert
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_count_by_user_id_zero(self, repository, mock_session):
        """Test counting returns 0 for user with no cards"""
        # Arrange
        user_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.count_by_user_id(user_id)

        # Assert
        assert result == 0
