"""
Unit tests for Response Envelope Schemas

Tests the response envelope schemas for standardized API responses.
"""

import pytest
from pydantic import ValidationError

from app.shared.presentation.schemas.response_envelope import (
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    ResponseEnvelope,
    SuccessResponse,
)


class TestErrorDetail:
    """Test ErrorDetail schema"""

    def test_create_error_detail(self):
        """Test creating error detail"""
        # Arrange & Act
        error = ErrorDetail(
            code="400_VALIDATION_FAILED",
            message="Validation failed",
            details={"field": "email", "issue": "invalid format"},
        )

        # Assert
        assert error.code == "400_VALIDATION_FAILED"
        assert error.message == "Validation failed"
        assert error.details["field"] == "email"

    def test_error_detail_with_empty_details(self):
        """Test error detail with empty details"""
        # Arrange & Act
        error = ErrorDetail(code="404_NOT_FOUND", message="Resource not found")

        # Assert
        assert error.details == {}

    def test_error_detail_validation(self):
        """Test error detail validation"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            ErrorDetail(message="Missing code")  # Missing required field


class TestPaginationMeta:
    """Test PaginationMeta schema"""

    def test_create_pagination_meta(self):
        """Test creating pagination metadata"""
        # Arrange & Act
        meta = PaginationMeta(total=100, page=1, page_size=10, total_pages=10)

        # Assert
        assert meta.total == 100
        assert meta.page == 1
        assert meta.page_size == 10
        assert meta.total_pages == 10

    def test_pagination_meta_validation_positive_total(self):
        """Test that total must be non-negative"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            PaginationMeta(total=-1, page=1, page_size=10, total_pages=0)

    def test_pagination_meta_validation_positive_page(self):
        """Test that page must be at least 1"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            PaginationMeta(total=100, page=0, page_size=10, total_pages=10)

    def test_pagination_meta_validation_positive_page_size(self):
        """Test that page_size must be at least 1"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            PaginationMeta(total=100, page=1, page_size=0, total_pages=10)

    def test_pagination_meta_zero_total(self):
        """Test pagination with zero total items"""
        # Arrange & Act
        meta = PaginationMeta(total=0, page=1, page_size=10, total_pages=0)

        # Assert
        assert meta.total == 0
        assert meta.total_pages == 0


class TestResponseEnvelope:
    """Test ResponseEnvelope schema"""

    def test_create_response_envelope_with_data(self):
        """Test creating response envelope with data"""
        # Arrange & Act
        response = ResponseEnvelope(data={"id": "123", "name": "Test"})

        # Assert
        assert response.data == {"id": "123", "name": "Test"}
        assert response.error is None
        assert response.meta is None

    def test_create_response_envelope_with_error(self):
        """Test creating response envelope with error"""
        # Arrange
        error = ErrorDetail(code="404_NOT_FOUND", message="Not found")

        # Act
        response = ResponseEnvelope(error=error)

        # Assert
        assert response.data is None
        assert response.error.code == "404_NOT_FOUND"
        assert response.meta is None

    def test_create_response_envelope_with_pagination(self):
        """Test creating response envelope with pagination"""
        # Arrange
        meta = PaginationMeta(total=100, page=2, page_size=10, total_pages=10)

        # Act
        response = ResponseEnvelope(data=[{"id": "1"}, {"id": "2"}], meta=meta)

        # Assert
        assert len(response.data) == 2
        assert response.meta.page == 2
        assert response.error is None


class TestSuccessResponse:
    """Test SuccessResponse schema"""

    def test_create_success_response(self):
        """Test creating success response"""
        # Arrange & Act
        response = SuccessResponse(data={"id": "123", "status": "active"})

        # Assert
        assert response.data == {"id": "123", "status": "active"}
        assert response.error is None
        assert response.meta is None

    def test_success_response_with_list(self):
        """Test success response with list data"""
        # Arrange & Act
        response = SuccessResponse(data=[{"id": "1"}, {"id": "2"}, {"id": "3"}])

        # Assert
        assert len(response.data) == 3
        assert response.error is None

    def test_success_response_with_string(self):
        """Test success response with string data"""
        # Arrange & Act
        response = SuccessResponse(data="Operation successful")

        # Assert
        assert response.data == "Operation successful"
        assert response.error is None

    def test_success_response_cannot_have_error(self):
        """Test that success response data field is required"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            SuccessResponse()  # Missing required data field


class TestPaginatedResponse:
    """Test PaginatedResponse schema"""

    def test_create_paginated_response(self):
        """Test creating paginated response"""
        # Arrange
        data = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        meta = PaginationMeta(total=30, page=1, page_size=3, total_pages=10)

        # Act
        response = PaginatedResponse(data=data, meta=meta)

        # Assert
        assert len(response.data) == 3
        assert response.meta.total == 30
        assert response.meta.page == 1
        assert response.error is None

    def test_paginated_response_empty_data(self):
        """Test paginated response with empty data"""
        # Arrange
        meta = PaginationMeta(total=0, page=1, page_size=10, total_pages=0)

        # Act
        response = PaginatedResponse(data=[], meta=meta)

        # Assert
        assert response.data == []
        assert response.meta.total == 0

    def test_paginated_response_requires_meta(self):
        """Test that paginated response requires meta"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            PaginatedResponse(data=[{"id": "1"}])  # Missing meta field

    def test_paginated_response_last_page(self):
        """Test paginated response for last page"""
        # Arrange
        data = [{"id": "91"}, {"id": "92"}]  # Only 2 items on last page
        meta = PaginationMeta(total=92, page=10, page_size=10, total_pages=10)

        # Act
        response = PaginatedResponse(data=data, meta=meta)

        # Assert
        assert len(response.data) == 2
        assert response.meta.page == 10
        assert response.meta.total_pages == 10


class TestErrorResponse:
    """Test ErrorResponse schema"""

    def test_create_error_response(self):
        """Test creating error response"""
        # Arrange
        error = ErrorDetail(
            code="500_INTERNAL_ERROR",
            message="Internal server error",
            details={"trace_id": "abc123"},
        )

        # Act
        response = ErrorResponse(error=error)

        # Assert
        assert response.data is None
        assert response.meta is None
        assert response.error.code == "500_INTERNAL_ERROR"
        assert response.error.message == "Internal server error"

    def test_error_response_validation_error(self):
        """Test error response for validation errors"""
        # Arrange
        error = ErrorDetail(
            code="400_VALIDATION_FAILED",
            message="Validation failed",
            details={
                "errors": [
                    {"field": "email", "message": "Invalid email format"},
                    {"field": "password", "message": "Password too short"},
                ]
            },
        )

        # Act
        response = ErrorResponse(error=error)

        # Assert
        assert response.error.code == "400_VALIDATION_FAILED"
        assert "errors" in response.error.details
        assert len(response.error.details["errors"]) == 2

    def test_error_response_requires_error(self):
        """Test that error response requires error field"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            ErrorResponse()  # Missing error field

    def test_error_response_404(self):
        """Test 404 error response"""
        # Arrange
        error = ErrorDetail(
            code="404_NOT_FOUND", message="Resource not found", details={"id": "123"}
        )

        # Act
        response = ErrorResponse(error=error)

        # Assert
        assert response.error.code == "404_NOT_FOUND"
        assert response.data is None

    def test_error_response_401(self):
        """Test 401 error response"""
        # Arrange
        error = ErrorDetail(
            code="401_UNAUTHORIZED",
            message="Authentication required",
            details={"reason": "Missing token"},
        )

        # Act
        response = ErrorResponse(error=error)

        # Assert
        assert response.error.code == "401_UNAUTHORIZED"
        assert response.error.details["reason"] == "Missing token"


class TestResponseEnvelopeIntegration:
    """Test response envelope integration scenarios"""

    def test_response_envelope_serialization(self):
        """Test that response envelope can be serialized"""
        # Arrange
        response = SuccessResponse(data={"id": "123", "name": "Test"})

        # Act
        json_data = response.model_dump()

        # Assert
        assert json_data["data"]["id"] == "123"
        assert json_data["error"] is None

    def test_response_envelope_json_schema(self):
        """Test that response envelope has valid JSON schema"""
        # Arrange & Act
        schema = ResponseEnvelope.model_json_schema()

        # Assert
        assert "properties" in schema
        assert "data" in schema["properties"]
        assert "error" in schema["properties"]
        assert "meta" in schema["properties"]

    def test_success_and_error_mutually_exclusive(self):
        """Test that having both data and error is allowed but semantically incorrect"""
        # Note: Pydantic allows this, but semantically we should not do this
        # This test documents the behavior
        # Arrange
        error = ErrorDetail(code="ERROR", message="Error")

        # Act
        response = ResponseEnvelope(data={"test": "data"}, error=error)

        # Assert
        assert response.data is not None
        assert response.error is not None
        # Both are present - this is allowed but should be avoided in practice
