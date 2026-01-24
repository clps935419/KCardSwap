"""
Unit tests for IdolSchemas

Tests Pydantic model validation for idol-related schemas.
"""

import pytest
from pydantic import ValidationError

from app.modules.identity.presentation.schemas.idol_schemas import (
    IdolGroupResponse,
    IdolGroupListResponse,
    IdolGroupListResponseWrapper,
)


class TestIdolGroupResponse:
    """Test IdolGroupResponse schema"""

    def test_create_idol_group_response(self):
        """Test creating idol group response with all fields"""
        # Arrange & Act
        group = IdolGroupResponse(
            id="newjeans",
            name="NewJeans",
            emoji="👖",
        )

        # Assert
        assert group.id == "newjeans"
        assert group.name == "NewJeans"
        assert group.emoji == "👖"

    def test_idol_group_response_missing_fields(self):
        """Test idol group response fails without required fields"""
        # Act & Assert
        with pytest.raises(ValidationError):
            IdolGroupResponse(id="newjeans")  # type: ignore


class TestIdolGroupListResponse:
    """Test IdolGroupListResponse schema"""

    def test_create_idol_group_list_response(self):
        """Test creating idol group list response"""
        # Arrange
        groups = [
            IdolGroupResponse(id="newjeans", name="NewJeans", emoji="👖"),
            IdolGroupResponse(id="ive", name="IVE", emoji="🦢"),
        ]

        # Act
        response = IdolGroupListResponse(groups=groups)

        # Assert
        assert len(response.groups) == 2
        assert response.groups[0].id == "newjeans"
        assert response.groups[1].id == "ive"

    def test_empty_idol_group_list(self):
        """Test creating empty idol group list"""
        # Arrange & Act
        response = IdolGroupListResponse(groups=[])

        # Assert
        assert len(response.groups) == 0


class TestIdolGroupListResponseWrapper:
    """Test IdolGroupListResponseWrapper schema"""

    def test_create_response_wrapper(self):
        """Test creating response wrapper"""
        # Arrange
        groups = [IdolGroupResponse(id="aespa", name="aespa", emoji="🦋")]
        data = IdolGroupListResponse(groups=groups)

        # Act
        wrapper = IdolGroupListResponseWrapper(data=data)

        # Assert
        assert len(wrapper.data.groups) == 1
        assert wrapper.meta is None
        assert wrapper.error is None

