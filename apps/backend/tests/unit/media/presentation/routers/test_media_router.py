"""
Unit tests for Media Router

Tests the media router endpoints with mocked use cases.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.media.presentation.routers.media_router import (
    attach_media_to_gallery_card,
    attach_media_to_post,
    confirm_upload,
    create_upload_url,
)
from app.modules.media.presentation.schemas.media_schemas import (
    AttachMediaToGalleryCardRequestSchema,
    AttachMediaToPostRequestSchema,
    CreateUploadUrlRequestSchema,
)


class TestMediaRouter:
    """Test Media Router endpoints"""

    @pytest.fixture
    def sample_user_id(self):
        """Create sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_media_id(self):
        """Create sample media ID"""
        return uuid4()

    @pytest.fixture
    def sample_post_id(self):
        """Create sample post ID"""
        return uuid4()

    @pytest.fixture
    def sample_card_id(self):
        """Create sample card ID"""
        return uuid4()

    @pytest.fixture
    def mock_injector(self):
        """Create mock injector"""
        return MagicMock()

    # Tests for POST /media/upload-url
    @pytest.mark.asyncio
    async def test_create_upload_url_success(
        self, sample_user_id, sample_media_id, mock_injector
    ):
        """Test successful upload URL creation"""
        # Arrange
        request = CreateUploadUrlRequestSchema(
            content_type="image/jpeg",
            file_size_bytes=1024000,
            filename="test.jpg",
        )

        mock_result = MagicMock()
        mock_result.media_id = sample_media_id
        mock_result.upload_url = "https://storage.googleapis.com/test/upload"
        mock_result.expires_in_minutes = 15

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_result
        mock_injector.get.return_value = mock_use_case

        # Act
        response = await create_upload_url(
            request=request,
            user_id=sample_user_id,
            injector=mock_injector,
        )

        # Assert
        assert response.media_id == sample_media_id
        assert response.upload_url == "https://storage.googleapis.com/test/upload"
        assert response.expires_in_minutes == 15
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_upload_url_invalid_content_type(
        self, sample_user_id, mock_injector
    ):
        """Test upload URL creation with invalid content type"""
        # Arrange
        request = CreateUploadUrlRequestSchema(
            content_type="application/pdf",
            file_size_bytes=1024000,
            filename="test.pdf",
        )

        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("Invalid content type")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(ValueError):
            await create_upload_url(
                request=request,
                user_id=sample_user_id,
                injector=mock_injector,
            )

    @pytest.mark.asyncio
    async def test_create_upload_url_file_too_large(
        self, sample_user_id, mock_injector
    ):
        """Test upload URL creation with file size exceeding limit"""
        # Arrange
        request = CreateUploadUrlRequestSchema(
            content_type="image/jpeg",
            file_size_bytes=10 * 1024 * 1024,  # 10MB
            filename="large.jpg",
        )

        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("File size exceeds limit")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(ValueError):
            await create_upload_url(
                request=request,
                user_id=sample_user_id,
                injector=mock_injector,
            )

    # Tests for POST /media/{media_id}/confirm
    @pytest.mark.asyncio
    async def test_confirm_upload_success(
        self, sample_user_id, sample_media_id, mock_injector
    ):
        """Test successful upload confirmation"""
        # Arrange
        mock_result = MagicMock()
        mock_result.media_id = sample_media_id
        mock_result.status = "confirmed"
        mock_result.file_size_bytes = 1024000

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_result
        mock_injector.get.return_value = mock_use_case

        # Act
        response = await confirm_upload(
            media_id=sample_media_id,
            user_id=sample_user_id,
            injector=mock_injector,
        )

        # Assert
        assert response.media_id == sample_media_id
        assert response.status == "confirmed"
        assert response.file_size_bytes == 1024000
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_upload_media_not_found(
        self, sample_user_id, sample_media_id, mock_injector
    ):
        """Test upload confirmation with non-existent media"""
        # Arrange
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("Media not found")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(ValueError):
            await confirm_upload(
                media_id=sample_media_id,
                user_id=sample_user_id,
                injector=mock_injector,
            )

    @pytest.mark.asyncio
    async def test_confirm_upload_not_owned(
        self, sample_user_id, sample_media_id, mock_injector
    ):
        """Test upload confirmation for media not owned by user"""
        # Arrange
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("Media not owned by user")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(ValueError):
            await confirm_upload(
                media_id=sample_media_id,
                user_id=sample_user_id,
                injector=mock_injector,
            )

    @pytest.mark.asyncio
    async def test_confirm_upload_quota_exceeded(
        self, sample_user_id, sample_media_id, mock_injector
    ):
        """Test upload confirmation with quota exceeded"""
        # Arrange
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = Exception("Quota exceeded")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(Exception):
            await confirm_upload(
                media_id=sample_media_id,
                user_id=sample_user_id,
                injector=mock_injector,
            )

    # Tests for POST /media/posts/{post_id}/attach
    @pytest.mark.asyncio
    async def test_attach_media_to_post_success(
        self, sample_user_id, sample_media_id, sample_post_id, mock_injector
    ):
        """Test successful media attachment to post"""
        # Arrange
        request = AttachMediaToPostRequestSchema(media_id=sample_media_id)

        mock_result = MagicMock()
        mock_result.media_id = sample_media_id
        mock_result.status = "attached"
        mock_result.attached_to = "post"
        mock_result.target_id = sample_post_id

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_result
        mock_injector.get.return_value = mock_use_case

        # Act
        response = await attach_media_to_post(
            post_id=sample_post_id,
            request=request,
            user_id=sample_user_id,
            injector=mock_injector,
        )

        # Assert
        assert response.media_id == sample_media_id
        assert response.status == "attached"
        assert response.attached_to == "post"
        assert response.target_id == sample_post_id
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_attach_media_to_post_not_confirmed(
        self, sample_user_id, sample_media_id, sample_post_id, mock_injector
    ):
        """Test media attachment to post with unconfirmed media"""
        # Arrange
        request = AttachMediaToPostRequestSchema(media_id=sample_media_id)

        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("Media not confirmed")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(ValueError):
            await attach_media_to_post(
                post_id=sample_post_id,
                request=request,
                user_id=sample_user_id,
                injector=mock_injector,
            )

    @pytest.mark.asyncio
    async def test_attach_media_to_post_not_owned(
        self, sample_user_id, sample_media_id, sample_post_id, mock_injector
    ):
        """Test media attachment to post with media not owned by user"""
        # Arrange
        request = AttachMediaToPostRequestSchema(media_id=sample_media_id)

        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("Media not owned by user")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(ValueError):
            await attach_media_to_post(
                post_id=sample_post_id,
                request=request,
                user_id=sample_user_id,
                injector=mock_injector,
            )

    # Tests for POST /media/gallery/cards/{card_id}/attach
    @pytest.mark.asyncio
    async def test_attach_media_to_gallery_card_success(
        self, sample_user_id, sample_media_id, sample_card_id, mock_injector
    ):
        """Test successful media attachment to gallery card"""
        # Arrange
        request = AttachMediaToGalleryCardRequestSchema(media_id=sample_media_id)

        mock_result = MagicMock()
        mock_result.media_id = sample_media_id
        mock_result.status = "attached"
        mock_result.attached_to = "gallery_card"
        mock_result.target_id = sample_card_id

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_result
        mock_injector.get.return_value = mock_use_case

        # Act
        response = await attach_media_to_gallery_card(
            card_id=sample_card_id,
            request=request,
            user_id=sample_user_id,
            injector=mock_injector,
        )

        # Assert
        assert response.media_id == sample_media_id
        assert response.status == "attached"
        assert response.attached_to == "gallery_card"
        assert response.target_id == sample_card_id
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_attach_media_to_gallery_card_not_confirmed(
        self, sample_user_id, sample_media_id, sample_card_id, mock_injector
    ):
        """Test media attachment to gallery card with unconfirmed media"""
        # Arrange
        request = AttachMediaToGalleryCardRequestSchema(media_id=sample_media_id)

        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("Media not confirmed")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(ValueError):
            await attach_media_to_gallery_card(
                card_id=sample_card_id,
                request=request,
                user_id=sample_user_id,
                injector=mock_injector,
            )

    @pytest.mark.asyncio
    async def test_attach_media_to_gallery_card_card_not_found(
        self, sample_user_id, sample_media_id, sample_card_id, mock_injector
    ):
        """Test media attachment to non-existent gallery card"""
        # Arrange
        request = AttachMediaToGalleryCardRequestSchema(media_id=sample_media_id)

        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("Gallery card not found")
        mock_injector.get.return_value = mock_use_case

        # Act & Assert
        with pytest.raises(ValueError):
            await attach_media_to_gallery_card(
                card_id=sample_card_id,
                request=request,
                user_id=sample_user_id,
                injector=mock_injector,
            )
