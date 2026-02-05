"""
Unit tests for Cards Router

Tests the cards router endpoints with mocked use cases.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modules.social.domain.value_objects.upload_quota import (
    QuotaExceededError,
    UploadQuota,
)
from app.modules.social.presentation.routers.cards_router import (
    confirm_card_upload,
    delete_card,
    get_my_cards,
    get_quota_status,
    get_upload_url,
)
from app.modules.social.presentation.schemas.card_schemas import (
    UploadCardRequest,
)


class TestCardsRouter:
    """Test Cards Router endpoints"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        return AsyncMock()

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_card_id(self):
        """Create sample card ID"""
        return uuid4()

    @pytest.fixture
    def mock_upload_quota(self):
        """Create mock upload quota"""
        return UploadQuota.from_mb_gb(
            daily_limit=10,
            max_file_mb=5,
            total_storage_gb=1,
        )

    @pytest.fixture
    def mock_upload_result(self, sample_card_id):
        """Create mock upload result"""
        result = MagicMock()
        result.upload_url = "https://storage.googleapis.com/test-bucket/test-file"
        result.method = "PUT"
        result.required_headers = {"Content-Type": "image/jpeg"}
        result.image_url = "https://cdn.example.com/cards/test-card.jpg"
        result.expires_at = datetime.now(timezone.utc)
        result.card_id = sample_card_id
        return result

    @pytest.fixture
    def mock_card(self, sample_card_id, sample_user_id):
        """Create mock card entity"""
        card = MagicMock()
        card.id = sample_card_id
        card.owner_id = sample_user_id
        card.idol = "Minji"
        card.idol_group = "NewJeans"
        card.album = "OMG"
        card.version = "Standard"
        card.rarity = "Common"
        card.status = "available"
        card.image_url = "https://cdn.example.com/cards/test-card.jpg"
        card.size_bytes = 1024000
        card.created_at = datetime.now(timezone.utc)
        card.updated_at = datetime.now(timezone.utc)
        return card

    # Tests for POST /cards/upload-url
    @pytest.mark.asyncio
    async def test_get_upload_url_success(
        self,
        mock_session,
        sample_user_id,
        mock_upload_quota,
        mock_upload_result,
    ):
        """Test successful upload URL generation"""
        # Arrange
        request = UploadCardRequest(
            content_type="image/jpeg",
            file_size_bytes=1024000,
            idol="Minji",
            idol_group="NewJeans",
            album="OMG",
            version="Standard",
            rarity="Common",
        )

        with patch(
            "app.modules.social.presentation.routers.cards_router.UploadCardUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_upload_result
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_upload_url(
                request=request,
                current_user_id=sample_user_id,
                session=mock_session,
                quota=mock_upload_quota,
            )

            # Assert
            assert response.data is not None
            assert response.data.upload_url == mock_upload_result.upload_url
            assert response.data.method == "PUT"
            assert response.data.card_id == mock_upload_result.card_id
            assert response.error is None
            mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_upload_url_quota_exceeded(
        self,
        mock_session,
        sample_user_id,
        mock_upload_quota,
    ):
        """Test upload URL generation with quota exceeded"""
        # Arrange
        request = UploadCardRequest(
            content_type="image/jpeg",
            file_size_bytes=1024000,
            idol="Minji",
            idol_group="NewJeans",
        )

        with patch(
            "app.modules.social.presentation.routers.cards_router.UploadCardUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = QuotaExceededError(
                "Daily upload limit exceeded", "daily_limit"
            )
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_upload_url(
                    request=request,
                    current_user_id=sample_user_id,
                    session=mock_session,
                    quota=mock_upload_quota,
                )

            assert exc_info.value.status_code == 422
            assert "LIMIT_EXCEEDED" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_upload_url_invalid_file_type(
        self,
        mock_session,
        sample_user_id,
        mock_upload_quota,
    ):
        """Test upload URL generation with invalid file type"""
        # Arrange
        request = UploadCardRequest(
            content_type="application/pdf",
            file_size_bytes=1024000,
            idol="Minji",
            idol_group="NewJeans",
        )

        with patch(
            "app.modules.social.presentation.routers.cards_router.UploadCardUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Invalid content type")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_upload_url(
                    request=request,
                    current_user_id=sample_user_id,
                    session=mock_session,
                    quota=mock_upload_quota,
                )

            assert exc_info.value.status_code == 400
            assert "VALIDATION_ERROR" in str(exc_info.value.detail)

    # Tests for GET /cards/me
    @pytest.mark.asyncio
    async def test_get_my_cards_success(
        self,
        mock_session,
        sample_user_id,
        mock_card,
    ):
        """Test successful retrieval of user's cards"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.GetMyCardsUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = [mock_card]
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_my_cards(
                current_user_id=sample_user_id,
                session=mock_session,
                status_filter=None,
            )

            # Assert
            assert response.data is not None
            assert len(response.data) == 1
            assert response.data[0].id == mock_card.id
            assert response.data[0].idol == "Minji"
            assert response.data[0].idol_group == "NewJeans"
            assert response.error is None
            mock_use_case.execute.assert_called_once_with(
                owner_id=sample_user_id, status=None
            )

    @pytest.mark.asyncio
    async def test_get_my_cards_with_status_filter(
        self,
        mock_session,
        sample_user_id,
        mock_card,
    ):
        """Test retrieval of user's cards with status filter"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.GetMyCardsUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = [mock_card]
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_my_cards(
                current_user_id=sample_user_id,
                session=mock_session,
                status_filter="available",
            )

            # Assert
            assert response.data is not None
            assert len(response.data) == 1
            mock_use_case.execute.assert_called_once_with(
                owner_id=sample_user_id, status="available"
            )

    @pytest.mark.asyncio
    async def test_get_my_cards_empty_list(
        self,
        mock_session,
        sample_user_id,
    ):
        """Test retrieval of user's cards when user has no cards"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.GetMyCardsUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = []
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_my_cards(
                current_user_id=sample_user_id,
                session=mock_session,
                status_filter=None,
            )

            # Assert
            assert response.data is not None
            assert len(response.data) == 0
            assert response.error is None

    # Tests for DELETE /cards/{card_id}
    @pytest.mark.asyncio
    async def test_delete_card_success(
        self,
        mock_session,
        sample_user_id,
        sample_card_id,
    ):
        """Test successful card deletion"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.DeleteCardUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = True
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await delete_card(
                card_id=sample_card_id,
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert response.data is not None
            assert response.data.success is True
            assert "deleted successfully" in response.data.message
            assert response.error is None
            mock_use_case.execute.assert_called_once_with(
                card_id=sample_card_id, owner_id=sample_user_id
            )

    @pytest.mark.asyncio
    async def test_delete_card_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_card_id,
    ):
        """Test card deletion when card not found"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.DeleteCardUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = False
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await delete_card(
                    card_id=sample_card_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 404
            assert "NOT_FOUND" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_delete_card_validation_error(
        self,
        mock_session,
        sample_user_id,
        sample_card_id,
    ):
        """Test card deletion with validation error (e.g., card in active trade)"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.DeleteCardUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError(
                "Cannot delete card in active trade"
            )
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await delete_card(
                    card_id=sample_card_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 400
            assert "VALIDATION_ERROR" in str(exc_info.value.detail)

    # Tests for GET /cards/quota/status
    @pytest.mark.asyncio
    async def test_get_quota_status_success(
        self,
        mock_session,
        sample_user_id,
        mock_upload_quota,
    ):
        """Test successful quota status retrieval"""
        # Arrange
        mock_status_result = MagicMock()
        mock_status_result.to_dict.return_value = {
            "uploads_today": 3,
            "daily_limit": 10,
            "storage_used_bytes": 3072000,
            "storage_limit_bytes": 1073741824,
            "remaining_uploads": 7,
            "remaining_storage_bytes": 1070669824,
            "storage_used_mb": 2.93,
            "storage_limit_mb": 1024.0,
            "remaining_storage_mb": 1021.07,
        }

        with patch(
            "app.modules.social.presentation.routers.cards_router.CheckUploadQuotaUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_status_result
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_quota_status(
                current_user_id=sample_user_id,
                session=mock_session,
                quota=mock_upload_quota,
            )

            # Assert
            assert response.data is not None
            assert response.data.uploads_today == 3
            assert response.data.daily_limit == 10
            assert response.data.remaining_uploads == 7
            assert response.error is None
            mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_quota_status_at_limit(
        self,
        mock_session,
        sample_user_id,
        mock_upload_quota,
    ):
        """Test quota status retrieval when at daily limit"""
        # Arrange
        mock_status_result = MagicMock()
        mock_status_result.to_dict.return_value = {
            "uploads_today": 10,
            "daily_limit": 10,
            "storage_used_bytes": 10485760,
            "storage_limit_bytes": 1073741824,
            "remaining_uploads": 0,
            "remaining_storage_bytes": 1063256064,
            "storage_used_mb": 10.0,
            "storage_limit_mb": 1024.0,
            "remaining_storage_mb": 1014.0,
        }

        with patch(
            "app.modules.social.presentation.routers.cards_router.CheckUploadQuotaUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_status_result
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await get_quota_status(
                current_user_id=sample_user_id,
                session=mock_session,
                quota=mock_upload_quota,
            )

            # Assert
            assert response.data is not None
            assert response.data.uploads_today == 10
            assert response.data.remaining_uploads == 0
            assert response.error is None

    # Tests for POST /cards/{card_id}/confirm-upload
    @pytest.mark.asyncio
    async def test_confirm_card_upload_success(
        self,
        mock_session,
        sample_user_id,
        sample_card_id,
    ):
        """Test successful card upload confirmation"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.ConfirmCardUploadUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = None
            mock_use_case_class.return_value = mock_use_case

            # Act
            response = await confirm_card_upload(
                card_id=sample_card_id,
                current_user_id=sample_user_id,
                session=mock_session,
            )

            # Assert
            assert response.data is not None
            assert response.data.success is True
            assert "confirmed successfully" in response.data.message
            assert response.error is None
            mock_use_case.execute.assert_called_once_with(
                card_id=sample_card_id, owner_id=sample_user_id
            )

    @pytest.mark.asyncio
    async def test_confirm_card_upload_card_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_card_id,
    ):
        """Test card upload confirmation when card not found"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.ConfirmCardUploadUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Card not found")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await confirm_card_upload(
                    card_id=sample_card_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 404
            assert "CARD_NOT_FOUND" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_confirm_card_upload_image_not_found(
        self,
        mock_session,
        sample_user_id,
        sample_card_id,
    ):
        """Test card upload confirmation when image not found in storage"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.ConfirmCardUploadUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError(
                "Image file not found in storage"
            )
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await confirm_card_upload(
                    card_id=sample_card_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 404
            assert "IMAGE_NOT_FOUND" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_confirm_card_upload_not_authorized(
        self,
        mock_session,
        sample_user_id,
        sample_card_id,
    ):
        """Test card upload confirmation when user not authorized"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.ConfirmCardUploadUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError(
                "Not authorized to confirm this card"
            )
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await confirm_card_upload(
                    card_id=sample_card_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 403
            assert "FORBIDDEN" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_confirm_card_upload_already_confirmed(
        self,
        mock_session,
        sample_user_id,
        sample_card_id,
    ):
        """Test card upload confirmation when already confirmed"""
        # Arrange
        with patch(
            "app.modules.social.presentation.routers.cards_router.ConfirmCardUploadUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Upload already confirmed")
            mock_use_case_class.return_value = mock_use_case

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await confirm_card_upload(
                    card_id=sample_card_id,
                    current_user_id=sample_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 400
            assert "VALIDATION_ERROR" in str(exc_info.value.detail)
