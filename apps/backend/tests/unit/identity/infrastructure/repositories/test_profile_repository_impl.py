"""
Unit tests for ProfileRepositoryImpl

Tests the profile repository implementation with mocked database session.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain.entities.profile import Profile
from app.modules.identity.infrastructure.database.models import ProfileModel
from app.modules.identity.infrastructure.repositories.profile_repository_impl import (
    ProfileRepositoryImpl,
)


class TestProfileRepositoryImpl:
    """Test ProfileRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return ProfileRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_profile(self):
        """Create sample Profile entity"""
        return Profile(
            id=uuid4(),
            user_id=uuid4(),
            nickname="TestUser",
            avatar_url="https://example.com/avatar.jpg",
            bio="Test bio",
            region="taipei",
            preferences={"theme": "dark"},
            privacy_flags={"show_online": True, "allow_stranger_chat": False},
            last_lat=25.0330,
            last_lng=121.5654,
            stealth_mode=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_profile_model(self, sample_profile):
        """Create sample ProfileModel"""
        return ProfileModel(
            id=sample_profile.id,
            user_id=sample_profile.user_id,
            nickname=sample_profile.nickname,
            avatar_url=sample_profile.avatar_url,
            bio=sample_profile.bio,
            region=sample_profile.region,
            preferences=sample_profile.preferences,
            privacy_flags=sample_profile.privacy_flags,
            last_lat=sample_profile.last_lat,
            last_lng=sample_profile.last_lng,
            stealth_mode=sample_profile.stealth_mode,
            created_at=sample_profile.created_at,
            updated_at=sample_profile.updated_at,
        )

    @pytest.mark.asyncio
    async def test_get_by_user_id_found(
        self, repository, mock_session, sample_profile_model
    ):
        """Test getting profile by user ID when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_profile_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_user_id(sample_profile_model.user_id)

        # Assert
        assert result is not None
        assert result.user_id == sample_profile_model.user_id
        assert result.nickname == sample_profile_model.nickname
        assert result.avatar_url == sample_profile_model.avatar_url
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_user_id_not_found(self, repository, mock_session):
        """Test getting profile by user ID when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.get_by_user_id(uuid4())

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_save_new_profile(self, repository, mock_session, sample_profile):
        """Test saving a new profile"""
        # Arrange
        # First query returns None (profile doesn't exist)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.save(sample_profile)

        # Assert
        assert result is not None
        assert result.user_id == sample_profile.user_id
        assert result.nickname == sample_profile.nickname
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_existing_profile(
        self, repository, mock_session, sample_profile, sample_profile_model
    ):
        """Test updating an existing profile"""
        # Arrange
        # Query returns existing model
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_profile_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Create modified profile
        updated_profile = Profile(
            id=sample_profile.id,
            user_id=sample_profile.user_id,
            nickname="UpdatedNickname",
            avatar_url=sample_profile.avatar_url,
            bio="Updated bio",
            region=sample_profile.region,
            preferences=sample_profile.preferences,
            privacy_flags=sample_profile.privacy_flags,
            last_lat=sample_profile.last_lat,
            last_lng=sample_profile.last_lng,
            stealth_mode=sample_profile.stealth_mode,
            created_at=sample_profile.created_at,
            updated_at=datetime.utcnow(),
        )

        # Act
        result = await repository.save(updated_profile)

        # Assert
        assert result is not None
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_with_default_privacy_flags(
        self, repository, mock_session, sample_profile
    ):
        """Test saving profile applies default privacy flags"""
        # Arrange
        profile_with_empty_flags = Profile(
            id=sample_profile.id,
            user_id=sample_profile.user_id,
            nickname=sample_profile.nickname,
            avatar_url=sample_profile.avatar_url,
            bio=sample_profile.bio,
            region=sample_profile.region,
            preferences=sample_profile.preferences,
            privacy_flags={},
            last_lat=sample_profile.last_lat,
            last_lng=sample_profile.last_lng,
            stealth_mode=sample_profile.stealth_mode,
            created_at=sample_profile.created_at,
            updated_at=sample_profile.updated_at,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.save(profile_with_empty_flags)

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_delete_existing_profile(
        self, repository, mock_session, sample_profile_model
    ):
        """Test deleting an existing profile"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_profile_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.delete(sample_profile_model.user_id)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_non_existing_profile(self, repository, mock_session):
        """Test deleting a non-existing profile"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.delete(uuid4())

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_to_entity_with_defaults(self, repository):
        """Test _to_entity applies default values correctly"""
        # Arrange
        model = ProfileModel(
            id=uuid4(),
            user_id=uuid4(),
            nickname="TestUser",
            avatar_url=None,
            bio=None,
            region="taipei",
            preferences=None,  # Should default to {}
            privacy_flags=None,  # Should get defaults
            last_lat=None,
            last_lng=None,
            stealth_mode=None,  # Should default to False
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Act
        entity = repository._to_entity(model)

        # Assert
        assert entity.preferences == {}
        assert entity.privacy_flags == {
            "show_online": True,
            "allow_stranger_chat": True,
        }
        assert entity.stealth_mode is False
