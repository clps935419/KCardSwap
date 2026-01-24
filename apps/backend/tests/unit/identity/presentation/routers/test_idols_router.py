"""
Unit tests for Idols Router

Tests the idols router endpoints.
"""

from unittest.mock import patch

import pytest

from app.modules.identity.infrastructure.data.idol_groups import IdolGroup
from app.modules.identity.presentation.routers.idols_router import get_idol_groups
from app.modules.identity.presentation.schemas.idol_schemas import (
    IdolGroupListResponseWrapper,
)


class TestIdolsRouter:
    """Test IdolsRouter endpoints"""

    @pytest.mark.asyncio
    async def test_get_idol_groups_returns_all_groups(self):
        """Test that get_idol_groups returns all idol groups"""
        # Arrange
        mock_groups = [
            IdolGroup(id="newjeans", name="NewJeans", emoji="👖", sort_order=1),
            IdolGroup(id="ive", name="IVE", emoji="🦢", sort_order=2),
            IdolGroup(id="aespa", name="aespa", emoji="🦋", sort_order=3),
        ]

        # Act
        with patch(
            "app.modules.identity.presentation.routers.idols_router.get_all_idol_groups",
            return_value=mock_groups,
        ):
            response = await get_idol_groups()

        # Assert
        assert isinstance(response, IdolGroupListResponseWrapper)
        assert response.data is not None
        assert len(response.data.groups) == 3
        assert response.data.groups[0].id == "newjeans"
        assert response.data.groups[0].name == "NewJeans"
        assert response.data.groups[0].emoji == "👖"
        assert response.meta is None
        assert response.error is None

    @pytest.mark.asyncio
    async def test_get_idol_groups_returns_correct_structure(self):
        """Test that get_idol_groups returns correct response structure"""
        # Arrange
        mock_groups = [
            IdolGroup(id="twice", name="TWICE", emoji="🍭", sort_order=1),
        ]

        # Act
        with patch(
            "app.modules.identity.presentation.routers.idols_router.get_all_idol_groups",
            return_value=mock_groups,
        ):
            response = await get_idol_groups()

        # Assert
        assert response.data.groups[0].id == "twice"
        assert response.data.groups[0].name == "TWICE"
        assert response.data.groups[0].emoji == "🍭"

    @pytest.mark.asyncio
    async def test_get_idol_groups_handles_empty_list(self):
        """Test that get_idol_groups handles empty list correctly"""
        # Arrange
        mock_groups = []

        # Act
        with patch(
            "app.modules.identity.presentation.routers.idols_router.get_all_idol_groups",
            return_value=mock_groups,
        ):
            response = await get_idol_groups()

        # Assert
        assert isinstance(response, IdolGroupListResponseWrapper)
        assert response.data is not None
        assert len(response.data.groups) == 0

    @pytest.mark.asyncio
    async def test_get_idol_groups_converts_domain_to_response(self):
        """Test that get_idol_groups converts domain models to response schemas"""
        # Arrange
        mock_groups = [
            IdolGroup(id="blackpink", name="BLACKPINK", emoji="💗", sort_order=1),
            IdolGroup(id="redvelvet", name="Red Velvet", emoji="🍰", sort_order=2),
        ]

        # Act
        with patch(
            "app.modules.identity.presentation.routers.idols_router.get_all_idol_groups",
            return_value=mock_groups,
        ):
            response = await get_idol_groups()

        # Assert
        assert len(response.data.groups) == 2
        # Verify first group
        assert response.data.groups[0].id == "blackpink"
        assert response.data.groups[0].name == "BLACKPINK"
        assert response.data.groups[0].emoji == "💗"
        # Verify second group
        assert response.data.groups[1].id == "redvelvet"
        assert response.data.groups[1].name == "Red Velvet"
        assert response.data.groups[1].emoji == "🍰"

    @pytest.mark.asyncio
    async def test_get_idol_groups_preserves_order(self):
        """Test that get_idol_groups preserves the order of groups"""
        # Arrange
        mock_groups = [
            IdolGroup(id="a", name="A", emoji="1️⃣", sort_order=1),
            IdolGroup(id="b", name="B", emoji="2️⃣", sort_order=2),
            IdolGroup(id="c", name="C", emoji="3️⃣", sort_order=3),
        ]

        # Act
        with patch(
            "app.modules.identity.presentation.routers.idols_router.get_all_idol_groups",
            return_value=mock_groups,
        ):
            response = await get_idol_groups()

        # Assert
        assert response.data.groups[0].id == "a"
        assert response.data.groups[1].id == "b"
        assert response.data.groups[2].id == "c"
