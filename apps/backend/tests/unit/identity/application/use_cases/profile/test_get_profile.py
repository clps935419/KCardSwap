"""
Unit tests for GetProfileUseCase

Tests the get profile use case with mocked dependencies.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.identity.application.use_cases.profile.get_profile import (
    GetProfileUseCase,
)
from app.modules.identity.domain.entities.profile import Profile


class TestGetProfileUseCase:
    """Test GetProfileUseCase"""

    @pytest.fixture
    def mock_profile_repo(self):
        """Create mock profile repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_profile_repo):
        """Create use case instance"""
        return GetProfileUseCase(profile_repo=mock_profile_repo)

    @pytest.fixture
    def sample_profile(self):
        """Create sample profile"""
        return Profile(
            user_id=uuid4(),
            display_name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            bio="Test bio",
            city_code="TPE",
        )

    @pytest.mark.asyncio
    async def test_get_profile_success(
        self, use_case, mock_profile_repo, sample_profile
    ):
        """Test successful profile retrieval"""
        # Arrange
        user_id = sample_profile.user_id
        mock_profile_repo.get_by_user_id.return_value = sample_profile

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert result is not None
        assert result.user_id == user_id
        assert result.display_name == "Test User"
        mock_profile_repo.get_by_user_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, use_case, mock_profile_repo):
        """Test profile retrieval when profile doesn't exist"""
        # Arrange
        user_id = uuid4()
        mock_profile_repo.get_by_user_id.return_value = None

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert result is None
        mock_profile_repo.get_by_user_id.assert_called_once_with(user_id)
