"""
Unit tests for Gallery Router

Tests the gallery router endpoints with mocked repositories.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modules.social.domain.entities.gallery_card import GalleryCard
from app.modules.social.presentation.routers.gallery_router import (
    create_gallery_card,
    delete_gallery_card,
    get_my_gallery_cards,
    get_user_gallery_cards,
    reorder_gallery_cards,
)
from app.modules.social.presentation.schemas.gallery_schemas import (
    CreateGalleryCardRequest,
    ReorderGalleryCardsRequest,
)


class TestGalleryRouter:
    """Test Gallery Router endpoints"""

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_card_id(self):
        """Create sample card ID"""
        return uuid4()

    @pytest.fixture
    def sample_other_user_id(self):
        """Create another sample user ID"""
        return uuid4()

    @pytest.fixture
    def mock_repository(self):
        """Create mock gallery card repository"""
        return AsyncMock()

    @pytest.fixture
    def sample_gallery_card(self, sample_card_id, sample_user_id):
        """Create sample gallery card"""
        card = GalleryCard(
            id=sample_card_id,
            user_id=sample_user_id,
            title="Minji PC",
            idol_name="Minji",
            era="OMG",
            description="Beautiful photocard",
            display_order=0,
        )
        card.created_at = datetime.now(timezone.utc)
        card.updated_at = datetime.now(timezone.utc)
        return card

    # Tests for GET /users/{user_id}/gallery/cards
    @pytest.mark.asyncio
    async def test_get_user_gallery_cards_success(
        self, sample_user_id, sample_other_user_id, mock_repository, sample_gallery_card
    ):
        """Test successful retrieval of another user's gallery cards"""
        # Arrange
        mock_repository.find_by_user_id.return_value = [sample_gallery_card]
        mock_repository.count_by_user_id.return_value = 1

        # Act
        response = await get_user_gallery_cards(
            user_id=sample_other_user_id,
            current_user_id=sample_user_id,
            repository=mock_repository,
        )

        # Assert
        assert response.total == 1
        assert len(response.items) == 1
        assert response.items[0].title == "Minji PC"
        assert response.items[0].idol_name == "Minji"
        mock_repository.find_by_user_id.assert_called_once_with(sample_other_user_id)
        mock_repository.count_by_user_id.assert_called_once_with(sample_other_user_id)

    @pytest.mark.asyncio
    async def test_get_user_gallery_cards_empty(
        self, sample_user_id, sample_other_user_id, mock_repository
    ):
        """Test retrieval of user's gallery cards when empty"""
        # Arrange
        mock_repository.find_by_user_id.return_value = []
        mock_repository.count_by_user_id.return_value = 0

        # Act
        response = await get_user_gallery_cards(
            user_id=sample_other_user_id,
            current_user_id=sample_user_id,
            repository=mock_repository,
        )

        # Assert
        assert response.total == 0
        assert len(response.items) == 0

    @pytest.mark.asyncio
    async def test_get_user_gallery_cards_error(
        self, sample_user_id, sample_other_user_id, mock_repository
    ):
        """Test error handling in get user gallery cards"""
        # Arrange
        mock_repository.find_by_user_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_user_gallery_cards(
                user_id=sample_other_user_id,
                current_user_id=sample_user_id,
                repository=mock_repository,
            )
        assert exc_info.value.status_code == 500

    # Tests for GET /gallery/cards/me
    @pytest.mark.asyncio
    async def test_get_my_gallery_cards_success(
        self, sample_user_id, mock_repository, sample_gallery_card
    ):
        """Test successful retrieval of own gallery cards"""
        # Arrange
        mock_repository.find_by_user_id.return_value = [sample_gallery_card]
        mock_repository.count_by_user_id.return_value = 1

        # Act
        response = await get_my_gallery_cards(
            current_user_id=sample_user_id,
            repository=mock_repository,
        )

        # Assert
        assert response.total == 1
        assert len(response.items) == 1
        assert response.items[0].id == sample_gallery_card.id
        mock_repository.find_by_user_id.assert_called_once_with(sample_user_id)

    @pytest.mark.asyncio
    async def test_get_my_gallery_cards_multiple(
        self, sample_user_id, mock_repository, sample_gallery_card
    ):
        """Test retrieval of multiple own gallery cards"""
        # Arrange
        card2 = GalleryCard(
            id=uuid4(),
            user_id=sample_user_id,
            title="Hanni PC",
            idol_name="Hanni",
            era="Ditto",
            description="Another card",
            display_order=1,
        )
        card2.created_at = datetime.now(timezone.utc)
        card2.updated_at = datetime.now(timezone.utc)

        mock_repository.find_by_user_id.return_value = [sample_gallery_card, card2]
        mock_repository.count_by_user_id.return_value = 2

        # Act
        response = await get_my_gallery_cards(
            current_user_id=sample_user_id,
            repository=mock_repository,
        )

        # Assert
        assert response.total == 2
        assert len(response.items) == 2

    # Tests for POST /gallery/cards
    @pytest.mark.asyncio
    async def test_create_gallery_card_success(
        self, sample_user_id, sample_card_id, mock_repository
    ):
        """Test successful gallery card creation"""
        # Arrange
        request = CreateGalleryCardRequest(
            title="Minji PC",
            idol_name="Minji",
            era="OMG",
            description="Beautiful photocard",
        )

        mock_repository.find_by_user_id.return_value = []

        created_card = GalleryCard(
            id=sample_card_id,
            user_id=sample_user_id,
            title=request.title,
            idol_name=request.idol_name,
            era=request.era,
            description=request.description,
            display_order=0,
        )
        created_card.created_at = datetime.now(timezone.utc)
        created_card.updated_at = datetime.now(timezone.utc)

        mock_repository.create.return_value = created_card

        # Act
        response = await create_gallery_card(
            request=request,
            current_user_id=sample_user_id,
            repository=mock_repository,
        )

        # Assert
        assert response.title == "Minji PC"
        assert response.idol_name == "Minji"
        assert response.display_order == 0
        mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_gallery_card_with_existing_cards(
        self, sample_user_id, sample_card_id, mock_repository, sample_gallery_card
    ):
        """Test gallery card creation with existing cards (proper ordering)"""
        # Arrange
        request = CreateGalleryCardRequest(
            title="Hanni PC",
            idol_name="Hanni",
            era="Ditto",
            description="Another card",
        )

        mock_repository.find_by_user_id.return_value = [sample_gallery_card]

        created_card = GalleryCard(
            id=uuid4(),
            user_id=sample_user_id,
            title=request.title,
            idol_name=request.idol_name,
            era=request.era,
            description=request.description,
            display_order=1,
        )
        created_card.created_at = datetime.now(timezone.utc)
        created_card.updated_at = datetime.now(timezone.utc)

        mock_repository.create.return_value = created_card

        # Act
        response = await create_gallery_card(
            request=request,
            current_user_id=sample_user_id,
            repository=mock_repository,
        )

        # Assert
        assert response.display_order == 1

    @pytest.mark.asyncio
    async def test_create_gallery_card_error(
        self, sample_user_id, mock_repository
    ):
        """Test error handling in gallery card creation"""
        # Arrange
        request = CreateGalleryCardRequest(
            title="Test Card",
            idol_name="Test",
            era="Test Era",
        )

        mock_repository.find_by_user_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_gallery_card(
                request=request,
                current_user_id=sample_user_id,
                repository=mock_repository,
            )
        assert exc_info.value.status_code == 500

    # Tests for DELETE /gallery/cards/{card_id}
    @pytest.mark.asyncio
    async def test_delete_gallery_card_success(
        self, sample_user_id, sample_card_id, mock_repository, sample_gallery_card
    ):
        """Test successful gallery card deletion"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_gallery_card
        mock_repository.delete.return_value = True

        # Act
        await delete_gallery_card(
            card_id=sample_card_id,
            current_user_id=sample_user_id,
            repository=mock_repository,
        )

        # Assert
        mock_repository.find_by_id.assert_called_once_with(sample_card_id)
        mock_repository.delete.assert_called_once_with(sample_card_id)

    @pytest.mark.asyncio
    async def test_delete_gallery_card_not_found(
        self, sample_user_id, sample_card_id, mock_repository
    ):
        """Test deletion of non-existent gallery card"""
        # Arrange
        mock_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_gallery_card(
                card_id=sample_card_id,
                current_user_id=sample_user_id,
                repository=mock_repository,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_gallery_card_not_owner(
        self, sample_user_id, sample_card_id, mock_repository, sample_gallery_card
    ):
        """Test deletion of gallery card by non-owner"""
        # Arrange
        other_user_id = uuid4()
        mock_repository.find_by_id.return_value = sample_gallery_card

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_gallery_card(
                card_id=sample_card_id,
                current_user_id=other_user_id,
                repository=mock_repository,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_gallery_card_delete_failed(
        self, sample_user_id, sample_card_id, mock_repository, sample_gallery_card
    ):
        """Test gallery card deletion failure"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_gallery_card
        mock_repository.delete.return_value = False

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_gallery_card(
                card_id=sample_card_id,
                current_user_id=sample_user_id,
                repository=mock_repository,
            )
        assert exc_info.value.status_code == 404

    # Tests for PUT /gallery/cards/reorder
    @pytest.mark.asyncio
    async def test_reorder_gallery_cards_success(
        self, sample_user_id, sample_card_id, mock_repository
    ):
        """Test successful gallery cards reordering"""
        # Arrange
        card_id_1 = uuid4()
        card_id_2 = uuid4()
        request = ReorderGalleryCardsRequest(card_ids=[card_id_2, card_id_1])

        updated_cards = [
            MagicMock(id=card_id_2, display_order=0),
            MagicMock(id=card_id_1, display_order=1),
        ]

        with patch(
            "app.modules.social.presentation.routers.gallery_router.ReorderGalleryCardsUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = updated_cards
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await reorder_gallery_cards(
                request=request,
                current_user_id=sample_user_id,
                repository=mock_repository,
            )

            # Assert
            assert response.message == "Gallery cards reordered successfully"
            assert response.updated_count == 2
            mock_use_case.execute.assert_called_once_with(
                sample_user_id, request.card_ids
            )

    @pytest.mark.asyncio
    async def test_reorder_gallery_cards_invalid_request(
        self, sample_user_id, mock_repository
    ):
        """Test reordering with invalid request"""
        # Arrange
        card_id = uuid4()
        request = ReorderGalleryCardsRequest(card_ids=[card_id])

        with patch(
            "app.modules.social.presentation.routers.gallery_router.ReorderGalleryCardsUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Invalid card IDs")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await reorder_gallery_cards(
                    request=request,
                    current_user_id=sample_user_id,
                    repository=mock_repository,
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_reorder_gallery_cards_error(
        self, sample_user_id, mock_repository
    ):
        """Test error handling in gallery cards reordering"""
        # Arrange
        request = ReorderGalleryCardsRequest(card_ids=[uuid4(), uuid4()])

        with patch(
            "app.modules.social.presentation.routers.gallery_router.ReorderGalleryCardsUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = Exception("Database error")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await reorder_gallery_cards(
                    request=request,
                    current_user_id=sample_user_id,
                    repository=mock_repository,
                )
            assert exc_info.value.status_code == 500
