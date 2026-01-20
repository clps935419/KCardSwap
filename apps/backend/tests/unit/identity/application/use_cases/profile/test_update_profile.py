"""
Unit tests for UpdateProfileUseCase

Tests the update profile use case with mocked dependencies.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.identity.application.use_cases.profile.update_profile import (
    UpdateProfileUseCase,
)
from app.modules.identity.domain.entities.profile import Profile


class TestUpdateProfileUseCase:
    """Test UpdateProfileUseCase"""

    @pytest.fixture
    def mock_profile_repo(self):
        """Create mock profile repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_profile_repo):
        """Create use case instance"""
        return UpdateProfileUseCase(profile_repo=mock_profile_repo)

    @pytest.fixture
    def sample_profile(self):
        """Create sample profile"""
        return Profile(
            user_id=uuid4(),
            nickname="Test User",
            avatar_url="https://example.com/avatar.jpg",
            bio="Test bio",
            region="TPE",
        )

    @pytest.mark.asyncio
    async def test_update_existing_profile(
        self, use_case, mock_profile_repo, sample_profile
    ):
        """Test updating an existing profile"""
        # Arrange
        user_id = sample_profile.user_id
        mock_profile_repo.get_by_user_id.return_value = sample_profile
        mock_profile_repo.save.return_value = sample_profile

        # Act
        result = await use_case.execute(
            user_id=user_id,
            nickname="New Name",
            bio="New bio",
        )

        # Assert
        assert result is not None
        mock_profile_repo.get_by_user_id.assert_called_once_with(user_id)
        mock_profile_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_new_profile_if_not_exists(
        self, use_case, mock_profile_repo
    ):
        """Test creating a new profile when it doesn't exist"""
        # Arrange
        user_id = uuid4()
        mock_profile_repo.get_by_user_id.return_value = None

        new_profile = Profile(user_id=user_id, nickname="New User")
        mock_profile_repo.save.return_value = new_profile

        # Act
        result = await use_case.execute(
            user_id=user_id,
            nickname="New User",
        )

        # Assert
        assert result is not None
        mock_profile_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_avatar_url(
        self, use_case, mock_profile_repo, sample_profile
    ):
        """Test updating avatar URL"""
        # Arrange
        user_id = sample_profile.user_id
        new_avatar_url = "https://example.com/new-avatar.jpg"
        mock_profile_repo.get_by_user_id.return_value = sample_profile
        mock_profile_repo.save.return_value = sample_profile

        # Act
        result = await use_case.execute(
            user_id=user_id,
            avatar_url=new_avatar_url,
        )

        # Assert
        assert result is not None
        mock_profile_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_bio(self, use_case, mock_profile_repo, sample_profile):
        """Test updating bio"""
        # Arrange
        user_id = sample_profile.user_id
        new_bio = "Updated bio text"
        mock_profile_repo.get_by_user_id.return_value = sample_profile
        mock_profile_repo.save.return_value = sample_profile

        # Act
        result = await use_case.execute(
            user_id=user_id,
            bio=new_bio,
        )

        # Assert
        assert result is not None
        mock_profile_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_region(
        self, use_case, mock_profile_repo, sample_profile
    ):
        """Test updating region"""
        # Arrange
        user_id = sample_profile.user_id
        new_region = "KHH"
        mock_profile_repo.get_by_user_id.return_value = sample_profile
        mock_profile_repo.save.return_value = sample_profile

        # Act
        result = await use_case.execute(
            user_id=user_id,
            region=new_region,
        )

        # Assert
        assert result is not None
        mock_profile_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_preferences(
        self, use_case, mock_profile_repo, sample_profile
    ):
        """Test updating preferences"""
        # Arrange
        user_id = sample_profile.user_id
        new_preferences = {"theme": "dark", "language": "zh-TW"}
        mock_profile_repo.get_by_user_id.return_value = sample_profile
        mock_profile_repo.save.return_value = sample_profile

        # Act
        result = await use_case.execute(
            user_id=user_id,
            preferences=new_preferences,
        )

        # Assert
        assert result is not None
        mock_profile_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_privacy_flags(
        self, use_case, mock_profile_repo, sample_profile
    ):
        """Test updating privacy flags"""
        # Arrange
        user_id = sample_profile.user_id
        new_privacy_flags = {"show_email": False, "show_location": True}
        mock_profile_repo.get_by_user_id.return_value = sample_profile
        mock_profile_repo.save.return_value = sample_profile

        # Act
        result = await use_case.execute(
            user_id=user_id,
            privacy_flags=new_privacy_flags,
        )

        # Assert
        assert result is not None
        mock_profile_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_multiple_fields(
        self, use_case, mock_profile_repo, sample_profile
    ):
        """Test updating multiple fields at once"""
        # Arrange
        user_id = sample_profile.user_id
        mock_profile_repo.get_by_user_id.return_value = sample_profile
        mock_profile_repo.save.return_value = sample_profile

        # Act
        result = await use_case.execute(
            user_id=user_id,
            nickname="Updated Name",
            bio="Updated bio",
            region="KHH",
            avatar_url="https://example.com/new-avatar.jpg",
        )

        # Assert
        assert result is not None
        mock_profile_repo.save.assert_called_once()
