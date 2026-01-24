"""
Unit tests for Card Schemas
Testing Pydantic model validation and serialization
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.modules.social.presentation.schemas.card_schemas import (
    CardListResponseWrapper,
    CardResponse,
    CardResponseWrapper,
    DeleteSuccessResponse,
    DeleteSuccessResponseWrapper,
    QuotaStatusResponse,
    QuotaStatusResponseWrapper,
    UploadCardRequest,
    UploadUrlResponse,
    UploadUrlResponseWrapper,
)


class TestUploadCardRequest:
    """Test UploadCardRequest schema"""

    def test_create_valid_request(self):
        """Test creating valid upload card request"""
        request = UploadCardRequest(
            content_type="image/jpeg",
            file_size_bytes=1234567,
            idol="IU",
            idol_group="Solo",
            album="Love Poem",
            version="Version A",
            rarity="rare",
        )

        assert request.content_type == "image/jpeg"
        assert request.file_size_bytes == 1234567
        assert request.idol == "IU"
        assert request.idol_group == "Solo"
        assert request.album == "Love Poem"
        assert request.version == "Version A"
        assert request.rarity == "rare"

    def test_create_minimal_request(self):
        """Test creating request with only required fields"""
        request = UploadCardRequest(content_type="image/png", file_size_bytes=500000)

        assert request.content_type == "image/png"
        assert request.file_size_bytes == 500000
        assert request.idol is None
        assert request.idol_group is None

    def test_invalid_file_size_zero(self):
        """Test that file size must be positive"""
        with pytest.raises(ValidationError):
            UploadCardRequest(content_type="image/jpeg", file_size_bytes=0)

    def test_invalid_file_size_negative(self):
        """Test that file size cannot be negative"""
        with pytest.raises(ValidationError):
            UploadCardRequest(content_type="image/jpeg", file_size_bytes=-100)

    def test_missing_required_fields(self):
        """Test that required fields must be provided"""
        with pytest.raises(ValidationError):
            UploadCardRequest()

    def test_idol_max_length(self):
        """Test idol name length validation"""
        # Should work with exactly 100 characters
        request = UploadCardRequest(
            content_type="image/jpeg", file_size_bytes=1000, idol="a" * 100
        )
        assert len(request.idol) == 100

        # Should fail with >100 characters
        with pytest.raises(ValidationError):
            UploadCardRequest(
                content_type="image/jpeg", file_size_bytes=1000, idol="a" * 101
            )


class TestUploadUrlResponse:
    """Test UploadUrlResponse schema"""

    def test_create_valid_response(self):
        """Test creating valid upload URL response"""
        card_id = uuid4()
        expires_at = datetime(2025, 1, 1, 0, 15, 0)

        response = UploadUrlResponse(
            upload_url="https://storage.googleapis.com/bucket/path",
            method="PUT",
            required_headers={"Content-Type": "image/jpeg"},
            image_url="https://storage.googleapis.com/bucket/cards/image.jpg",
            expires_at=expires_at,
            card_id=card_id,
        )

        assert "storage.googleapis.com" in response.upload_url
        assert response.method == "PUT"
        assert response.required_headers["Content-Type"] == "image/jpeg"
        assert response.card_id == card_id
        assert response.expires_at == expires_at

    def test_serialization(self):
        """Test schema serialization to dict"""
        card_id = uuid4()
        response = UploadUrlResponse(
            upload_url="https://test.com",
            method="PUT",
            required_headers={},
            image_url="https://test.com/image.jpg",
            expires_at=datetime(2025, 1, 1),
            card_id=card_id,
        )

        data = response.model_dump()
        assert data["upload_url"] == "https://test.com"
        assert data["card_id"] == card_id


class TestCardResponse:
    """Test CardResponse schema"""

    def test_create_valid_response(self):
        """Test creating valid card response"""
        card_id = uuid4()
        owner_id = uuid4()
        now = datetime.utcnow()

        response = CardResponse(
            id=card_id,
            owner_id=owner_id,
            idol="IU",
            idol_group="Solo",
            album="Love Poem",
            version="Version A",
            rarity="rare",
            status="available",
            image_url="https://test.com/image.jpg",
            size_bytes=1234567,
            created_at=now,
            updated_at=now,
        )

        assert response.id == card_id
        assert response.owner_id == owner_id
        assert response.idol == "IU"
        assert response.status == "available"

    def test_optional_fields_can_be_none(self):
        """Test that optional fields can be None"""
        response = CardResponse(
            id=uuid4(),
            owner_id=uuid4(),
            idol=None,
            idol_group=None,
            album=None,
            version=None,
            rarity=None,
            status="available",
            image_url=None,
            size_bytes=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert response.idol is None
        assert response.idol_group is None
        assert response.image_url is None


class TestQuotaStatusResponse:
    """Test QuotaStatusResponse schema"""

    def test_create_valid_response(self):
        """Test creating valid quota status response"""
        response = QuotaStatusResponse(
            uploads_today=1,
            daily_limit=2,
            remaining_uploads=1,
            storage_used_bytes=5242880,
            storage_limit_bytes=1073741824,
            remaining_storage_bytes=1068498944,
            storage_used_mb=5.0,
            storage_limit_mb=1024.0,
            remaining_storage_mb=1019.0,
        )

        assert response.uploads_today == 1
        assert response.daily_limit == 2
        assert response.remaining_uploads == 1
        assert response.storage_used_mb == 5.0

    def test_quota_calculations(self):
        """Test quota calculations are correct"""
        response = QuotaStatusResponse(
            uploads_today=5,
            daily_limit=10,
            remaining_uploads=5,
            storage_used_bytes=1048576,  # 1 MB
            storage_limit_bytes=10485760,  # 10 MB
            remaining_storage_bytes=9437184,
            storage_used_mb=1.0,
            storage_limit_mb=10.0,
            remaining_storage_mb=9.0,
        )

        assert response.uploads_today + response.remaining_uploads == response.daily_limit
        assert response.storage_used_mb == 1.0


class TestUploadUrlResponseWrapper:
    """Test UploadUrlResponseWrapper schema"""

    def test_create_wrapper(self):
        """Test creating response wrapper"""
        data = UploadUrlResponse(
            upload_url="https://test.com",
            method="PUT",
            required_headers={},
            image_url="https://test.com/image.jpg",
            expires_at=datetime(2025, 1, 1),
            card_id=uuid4(),
        )

        wrapper = UploadUrlResponseWrapper(data=data)

        assert wrapper.data == data
        assert wrapper.meta is None
        assert wrapper.error is None


class TestCardResponseWrapper:
    """Test CardResponseWrapper schema"""

    def test_create_wrapper(self):
        """Test creating card response wrapper"""
        data = CardResponse(
            id=uuid4(),
            owner_id=uuid4(),
            status="available",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        wrapper = CardResponseWrapper(data=data)

        assert wrapper.data == data
        assert wrapper.meta is None
        assert wrapper.error is None


class TestCardListResponseWrapper:
    """Test CardListResponseWrapper schema"""

    def test_create_wrapper_with_list(self):
        """Test creating wrapper with card list"""
        cards = [
            CardResponse(
                id=uuid4(),
                owner_id=uuid4(),
                status="available",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for _ in range(3)
        ]

        wrapper = CardListResponseWrapper(data=cards)

        assert len(wrapper.data) == 3
        assert wrapper.meta is None

    def test_create_wrapper_with_empty_list(self):
        """Test creating wrapper with empty list"""
        wrapper = CardListResponseWrapper(data=[])

        assert wrapper.data == []
        assert wrapper.meta is None


class TestQuotaStatusResponseWrapper:
    """Test QuotaStatusResponseWrapper schema"""

    def test_create_wrapper(self):
        """Test creating quota status wrapper"""
        data = QuotaStatusResponse(
            uploads_today=1,
            daily_limit=2,
            remaining_uploads=1,
            storage_used_bytes=1000,
            storage_limit_bytes=10000,
            remaining_storage_bytes=9000,
            storage_used_mb=0.001,
            storage_limit_mb=0.01,
            remaining_storage_mb=0.009,
        )

        wrapper = QuotaStatusResponseWrapper(data=data)

        assert wrapper.data == data


class TestDeleteSuccessResponse:
    """Test DeleteSuccessResponse schema"""

    def test_create_success_response(self):
        """Test creating delete success response"""
        response = DeleteSuccessResponse(
            success=True, message="Card deleted successfully"
        )

        assert response.success is True
        assert response.message == "Card deleted successfully"

    def test_default_success_value(self):
        """Test that success defaults to True"""
        response = DeleteSuccessResponse(message="Deleted")

        assert response.success is True


class TestDeleteSuccessResponseWrapper:
    """Test DeleteSuccessResponseWrapper schema"""

    def test_create_wrapper(self):
        """Test creating delete success wrapper"""
        data = DeleteSuccessResponse(success=True, message="Deleted")
        wrapper = DeleteSuccessResponseWrapper(data=data)

        assert wrapper.data.success is True
        assert wrapper.data.message == "Deleted"
        assert wrapper.meta is None


class TestSchemaExamples:
    """Test that schema examples are valid"""

    def test_upload_card_request_example(self):
        """Test that UploadCardRequest example is valid"""
        example = {
            "content_type": "image/jpeg",
            "file_size_bytes": 1234567,
            "idol": "IU",
            "idol_group": "Solo",
            "album": "Love Poem",
            "version": "Version A",
            "rarity": "rare",
        }

        request = UploadCardRequest(**example)
        assert request.content_type == "image/jpeg"

    def test_quota_status_response_example(self):
        """Test that QuotaStatusResponse example is valid"""
        example = {
            "uploads_today": 1,
            "daily_limit": 2,
            "remaining_uploads": 1,
            "storage_used_bytes": 5242880,
            "storage_limit_bytes": 1073741824,
            "remaining_storage_bytes": 1068498944,
            "storage_used_mb": 5.0,
            "storage_limit_mb": 1024.0,
            "remaining_storage_mb": 1019.0,
        }

        response = QuotaStatusResponse(**example)
        assert response.uploads_today == 1
