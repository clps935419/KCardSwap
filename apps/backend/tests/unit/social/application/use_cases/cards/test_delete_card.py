"""
Unit tests for DeleteCardUseCase
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.cards.delete_card import (
    DeleteCardUseCase,
)
from app.modules.social.domain.entities.card import Card


class TestDeleteCardUseCase:
    """Test DeleteCardUseCase"""

    @pytest.fixture
    def mock_card_repository(self):
        """Create mock card repository"""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def mock_gcs_service(self):
        """Create mock GCS service"""
        service = Mock()
        return service

    @pytest.fixture
    def use_case(self, mock_card_repository, mock_gcs_service):
        """Create use case instance"""
        return DeleteCardUseCase(
            card_repository=mock_card_repository,
            gcs_service=mock_gcs_service,
        )

    @pytest.mark.asyncio
    async def test_delete_card_success(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test successful card deletion"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        image_url = (
            "https://storage.googleapis.com/my-bucket/cards/user123/card456.jpg"
        )

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=image_url,
            status=Card.STATUS_AVAILABLE,
        )

        mock_card_repository.find_by_id.return_value = card
        mock_card_repository.delete.return_value = True
        mock_gcs_service.delete_blob.return_value = None

        # Act
        result = await use_case.execute(card_id=card_id, owner_id=owner_id)

        # Assert
        assert result is True
        mock_card_repository.find_by_id.assert_called_once_with(card_id)
        mock_card_repository.delete.assert_called_once_with(card_id)
        mock_gcs_service.delete_blob.assert_called_once_with("cards/user123/card456.jpg")

    @pytest.mark.asyncio
    async def test_delete_card_not_found(self, use_case, mock_card_repository):
        """Test deletion when card not found"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        mock_card_repository.find_by_id.return_value = None

        # Act
        result = await use_case.execute(card_id=card_id, owner_id=owner_id)

        # Assert
        assert result is False
        mock_card_repository.find_by_id.assert_called_once_with(card_id)
        mock_card_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_card_not_owner(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test deletion when user is not the card owner"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        different_user_id = uuid4()

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url="https://storage.googleapis.com/bucket/cards/user/card.jpg",
        )

        mock_card_repository.find_by_id.return_value = card

        # Act
        result = await use_case.execute(card_id=card_id, owner_id=different_user_id)

        # Assert
        assert result is False
        mock_card_repository.find_by_id.assert_called_once_with(card_id)
        mock_card_repository.delete.assert_not_called()
        mock_gcs_service.delete_blob.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_card_in_trading_raises_error(
        self, use_case, mock_card_repository
    ):
        """Test that deleting a card in trading status raises ValueError"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()

        card = Card(
            id=card_id,
            owner_id=owner_id,
            status=Card.STATUS_TRADING,
            image_url="https://storage.googleapis.com/bucket/cards/user/card.jpg",
        )

        mock_card_repository.find_by_id.return_value = card

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot delete card that is currently in a trade"
        ):
            await use_case.execute(card_id=card_id, owner_id=owner_id)

        mock_card_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_card_without_image_url(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test deletion when card has no image URL"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=None,
            status=Card.STATUS_AVAILABLE,
        )

        mock_card_repository.find_by_id.return_value = card
        mock_card_repository.delete.return_value = True

        # Act
        result = await use_case.execute(card_id=card_id, owner_id=owner_id)

        # Assert
        assert result is True
        mock_card_repository.delete.assert_called_once_with(card_id)
        mock_gcs_service.delete_blob.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_card_gcs_deletion_fails_continues(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test that card deletion continues even if GCS deletion fails"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        image_url = "https://storage.googleapis.com/bucket/cards/user/card.jpg"

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=image_url,
            status=Card.STATUS_AVAILABLE,
        )

        mock_card_repository.find_by_id.return_value = card
        mock_card_repository.delete.return_value = True
        mock_gcs_service.delete_blob.side_effect = Exception("GCS error")

        # Act
        result = await use_case.execute(card_id=card_id, owner_id=owner_id)

        # Assert
        assert result is True
        mock_card_repository.delete.assert_called_once_with(card_id)

    @pytest.mark.asyncio
    async def test_delete_card_malformed_url(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test deletion with malformed image URL"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        # URL without expected structure
        image_url = "http://example.com/image.jpg"

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=image_url,
            status=Card.STATUS_AVAILABLE,
        )

        mock_card_repository.find_by_id.return_value = card
        mock_card_repository.delete.return_value = True

        # Act
        result = await use_case.execute(card_id=card_id, owner_id=owner_id)

        # Assert
        assert result is True
        mock_card_repository.delete.assert_called_once_with(card_id)
        # Should not call GCS delete with malformed URL
        mock_gcs_service.delete_blob.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_traded_card_success(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test that traded cards can be deleted"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        image_url = "https://storage.googleapis.com/bucket/cards/user/card.jpg"

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=image_url,
            status=Card.STATUS_TRADED,
        )

        mock_card_repository.find_by_id.return_value = card
        mock_card_repository.delete.return_value = True
        mock_gcs_service.delete_blob.return_value = None

        # Act
        result = await use_case.execute(card_id=card_id, owner_id=owner_id)

        # Assert
        assert result is True
        mock_card_repository.delete.assert_called_once_with(card_id)

    @pytest.mark.asyncio
    async def test_delete_card_extracts_blob_name_correctly(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test that blob name is extracted correctly from various URL formats"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        image_url = "https://storage.googleapis.com/my-bucket/cards/nested/path/file.jpg"

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=image_url,
            status=Card.STATUS_AVAILABLE,
        )

        mock_card_repository.find_by_id.return_value = card
        mock_card_repository.delete.return_value = True

        # Act
        await use_case.execute(card_id=card_id, owner_id=owner_id)

        # Assert
        # Should extract "cards/nested/path/file.jpg"
        mock_gcs_service.delete_blob.assert_called_once_with(
            "cards/nested/path/file.jpg"
        )
