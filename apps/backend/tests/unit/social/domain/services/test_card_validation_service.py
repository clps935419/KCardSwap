"""
Unit tests for CardValidationService

Tests the card validation domain service.
"""

import pytest

from app.modules.social.domain.services.card_validation_service import (
    CardValidationService,
)


class TestCardValidationService:
    """Test CardValidationService"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return CardValidationService()

    def test_validate_content_type_jpeg(self, service):
        """Test validating JPEG content type"""
        assert service.validate_content_type("image/jpeg") is True

    def test_validate_content_type_png(self, service):
        """Test validating PNG content type"""
        assert service.validate_content_type("image/png") is True

    def test_validate_content_type_case_insensitive(self, service):
        """Test content type validation is case insensitive"""
        assert service.validate_content_type("IMAGE/JPEG") is True
        assert service.validate_content_type("Image/Png") is True

    def test_validate_content_type_invalid(self, service):
        """Test validation rejects invalid content types"""
        assert service.validate_content_type("image/gif") is False
        assert service.validate_content_type("image/bmp") is False
        assert service.validate_content_type("video/mp4") is False
        assert service.validate_content_type("application/pdf") is False

    def test_validate_file_size_within_limit(self, service):
        """Test validation accepts files within size limit"""
        max_size = 10 * 1024 * 1024  # 10MB
        assert service.validate_file_size(5 * 1024 * 1024, max_size) is True
        assert service.validate_file_size(max_size, max_size) is True

    def test_validate_file_size_exceeds_limit(self, service):
        """Test validation rejects files exceeding size limit"""
        max_size = 10 * 1024 * 1024  # 10MB
        assert service.validate_file_size(15 * 1024 * 1024, max_size) is False

    def test_validate_file_size_zero_or_negative(self, service):
        """Test validation rejects zero or negative file sizes"""
        max_size = 10 * 1024 * 1024
        assert service.validate_file_size(0, max_size) is False
        assert service.validate_file_size(-100, max_size) is False

    def test_get_file_extension_jpeg(self, service):
        """Test getting file extension for JPEG"""
        assert service.get_file_extension("image/jpeg") == ".jpg"

    def test_get_file_extension_png(self, service):
        """Test getting file extension for PNG"""
        assert service.get_file_extension("image/png") == ".png"

    def test_get_file_extension_case_insensitive(self, service):
        """Test getting file extension is case insensitive"""
        assert service.get_file_extension("IMAGE/JPEG") == ".jpg"
        assert service.get_file_extension("Image/Png") == ".png"

    def test_get_file_extension_unsupported(self, service):
        """Test getting file extension for unsupported type raises error"""
        with pytest.raises(ValueError, match="Unsupported content type"):
            service.get_file_extension("image/gif")

    def test_validate_upload_request_success(self, service):
        """Test successful upload request validation"""
        is_valid, error = service.validate_upload_request(
            content_type="image/jpeg",
            file_size_bytes=5 * 1024 * 1024,  # 5MB
            max_file_size_bytes=10 * 1024 * 1024,  # 10MB
        )
        assert is_valid is True
        assert error == ""

    def test_validate_upload_request_invalid_content_type(self, service):
        """Test upload request validation with invalid content type"""
        is_valid, error = service.validate_upload_request(
            content_type="image/gif",
            file_size_bytes=5 * 1024 * 1024,
            max_file_size_bytes=10 * 1024 * 1024,
        )
        assert is_valid is False
        assert "Invalid content type" in error
        assert "image/jpeg" in error
        assert "image/png" in error

    def test_validate_upload_request_file_too_large(self, service):
        """Test upload request validation with oversized file"""
        is_valid, error = service.validate_upload_request(
            content_type="image/jpeg",
            file_size_bytes=15 * 1024 * 1024,  # 15MB
            max_file_size_bytes=10 * 1024 * 1024,  # 10MB
        )
        assert is_valid is False
        assert "exceeds limit" in error
        assert "10.0MB" in error

    def test_validate_upload_request_file_zero_size(self, service):
        """Test upload request validation with zero-sized file"""
        is_valid, error = service.validate_upload_request(
            content_type="image/jpeg",
            file_size_bytes=0,
            max_file_size_bytes=10 * 1024 * 1024,
        )
        assert is_valid is False
        assert "exceeds limit" in error

    def test_allowed_content_types_constant(self, service):
        """Test ALLOWED_CONTENT_TYPES constant"""
        assert "image/jpeg" in service.ALLOWED_CONTENT_TYPES
        assert "image/png" in service.ALLOWED_CONTENT_TYPES
        assert len(service.ALLOWED_CONTENT_TYPES) == 2

    def test_content_type_extensions_mapping(self, service):
        """Test CONTENT_TYPE_EXTENSIONS mapping"""
        assert ".jpg" in service.CONTENT_TYPE_EXTENSIONS["image/jpeg"]
        assert ".jpeg" in service.CONTENT_TYPE_EXTENSIONS["image/jpeg"]
        assert ".png" in service.CONTENT_TYPE_EXTENSIONS["image/png"]
