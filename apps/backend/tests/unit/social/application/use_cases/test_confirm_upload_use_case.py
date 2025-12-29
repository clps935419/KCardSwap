"""
Unit tests for ConfirmCardUploadUseCase
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.cards.confirm_upload import (
    ConfirmCardUploadUseCase,
)
from app.modules.social.domain.entities.card import Card


class TestConfirmCardUploadUseCase:
    """Test ConfirmCardUploadUseCase"""

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
        return ConfirmCardUploadUseCase(
            card_repository=mock_card_repository,
            gcs_service=mock_gcs_service,
        )

    @pytest.mark.asyncio
    async def test_confirm_upload_success(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test successful upload confirmation"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        image_url = "https://storage.googleapis.com/bucket/cards/user123/card456.jpg"

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=image_url,
            size_bytes=1024 * 500,
        )

        mock_card_repository.find_by_id.return_value = card
        mock_gcs_service.blob_exists.return_value = True
        mock_card_repository.save.return_value = card

        # Act
        result = await use_case.execute(card_id=card_id, owner_id=owner_id)

        # Assert
        assert result is True
        assert card.is_upload_confirmed()
        mock_card_repository.find_by_id.assert_called_once_with(card_id)
        mock_gcs_service.blob_exists.assert_called_once_with(
            "cards/user123/card456.jpg"
        )
        mock_card_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_upload_card_not_found(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test confirmation when card not found"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        mock_card_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Card not found"):
            await use_case.execute(card_id=card_id, owner_id=owner_id)

    @pytest.mark.asyncio
    async def test_confirm_upload_not_owner(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test confirmation when user is not the card owner"""
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

        # Act & Assert
        with pytest.raises(ValueError, match="Not authorized"):
            await use_case.execute(card_id=card_id, owner_id=different_user_id)

    @pytest.mark.asyncio
    async def test_confirm_upload_already_confirmed(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test confirmation when upload already confirmed"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url="https://storage.googleapis.com/bucket/cards/user/card.jpg",
        )
        card.confirm_upload()  # Already confirmed

        mock_card_repository.find_by_id.return_value = card

        # Act & Assert
        with pytest.raises(ValueError, match="Upload already confirmed"):
            await use_case.execute(card_id=card_id, owner_id=owner_id)

    @pytest.mark.asyncio
    async def test_confirm_upload_no_image_url(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test confirmation when card has no image URL"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=None,
        )

        mock_card_repository.find_by_id.return_value = card

        # Act & Assert
        with pytest.raises(ValueError, match="Card has no image URL"):
            await use_case.execute(card_id=card_id, owner_id=owner_id)

    @pytest.mark.asyncio
    async def test_confirm_upload_image_not_in_storage(
        self, use_case, mock_card_repository, mock_gcs_service
    ):
        """Test confirmation when image file doesn't exist in GCS"""
        # Arrange
        card_id = uuid4()
        owner_id = uuid4()
        image_url = "https://storage.googleapis.com/bucket/cards/user/card.jpg"

        card = Card(
            id=card_id,
            owner_id=owner_id,
            image_url=image_url,
        )

        mock_card_repository.find_by_id.return_value = card
        mock_gcs_service.blob_exists.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match="Image file not found in storage"):
            await use_case.execute(card_id=card_id, owner_id=owner_id)

    def test_extract_blob_name_from_gcs_url(self, use_case):
        """Test extracting blob name from GCS URL"""
        # Standard GCS public URL
        url = "https://storage.googleapis.com/my-bucket/cards/user123/card456.jpg"
        blob_name = use_case._extract_blob_name(url)
        assert blob_name == "cards/user123/card456.jpg"

    def test_extract_blob_name_from_nested_path(self, use_case):
        """Test extracting blob name with nested path"""
        url = "https://storage.googleapis.com/bucket/path/to/nested/file.jpg"
        blob_name = use_case._extract_blob_name(url)
        assert blob_name == "path/to/nested/file.jpg"

    def test_extract_blob_name_fallback(self, use_case):
        """Test fallback when URL doesn't match expected format"""
        # If URL doesn't contain storage.googleapis.com, return as-is
        url = "some/blob/name.jpg"
        blob_name = use_case._extract_blob_name(url)
        assert blob_name == "some/blob/name.jpg"
