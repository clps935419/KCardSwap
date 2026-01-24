"""
Unit tests for Profile Router

Tests for GET /profile/me and PUT /profile/me endpoints.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import HTTPException, status

from app.modules.identity.domain.entities.profile import Profile
from app.modules.identity.presentation.routers.profile_router import (
    get_my_profile,
    update_my_profile,
)
from app.modules.identity.presentation.schemas.profile_schemas import (
    UpdateProfileRequest,
)


class TestGetMyProfile:
    """Tests for GET /profile/me endpoint"""

    @pytest.fixture
    def mock_current_user(self):
        """Mock authenticated user ID"""
        return uuid4()

    @pytest.fixture
    def sample_profile(self, mock_current_user):
        """Sample profile entity"""
        return Profile(
            id=uuid4(),
            user_id=mock_current_user,
            nickname="TestUser",
            avatar_url="https://example.com/avatar.jpg",
            bio="Test bio",
            region="TW",
            preferences={"lang": "zh-TW"},
            privacy_flags={"show_online": True, "allow_stranger_chat": True, "nearby_visible": True},
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 2, 12, 0, 0),
        )

    @pytest.mark.asyncio
    async def test_get_my_profile_success(self, mock_current_user, sample_profile):
        """Test successful profile retrieval"""
        # Arrange
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = sample_profile

        # Act
        response = await get_my_profile(
            current_user_id=mock_current_user,
            use_case=mock_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.id == sample_profile.id
        assert response.data.user_id == sample_profile.user_id
        assert response.data.nickname == "TestUser"
        assert response.data.avatar_url == "https://example.com/avatar.jpg"
        assert response.data.bio == "Test bio"
        assert response.data.region == "TW"
        assert response.data.preferences == {"lang": "zh-TW"}
        assert response.data.privacy_flags["show_online"] is True
        assert response.data.privacy_flags["allow_stranger_chat"] is True
        assert response.error is None
        
        # Verify use case was called correctly
        mock_use_case.execute.assert_called_once_with(mock_current_user)

    @pytest.mark.asyncio
    async def test_get_my_profile_not_found(self, mock_current_user):
        """Test profile not found raises HTTPException"""
        # Arrange
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_my_profile(
                current_user_id=mock_current_user,
                use_case=mock_use_case,
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "NOT_FOUND" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_my_profile_with_default_privacy_flags(self, mock_current_user):
        """Test profile with None privacy_flags gets default values"""
        # Arrange
        profile_without_privacy = Profile(
            id=uuid4(),
            user_id=mock_current_user,
            nickname="TestUser",
            avatar_url=None,
            bio=None,
            region="TW",
            preferences=None,
            privacy_flags=None,  # None privacy flags
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = profile_without_privacy

        # Act
        response = await get_my_profile(
            current_user_id=mock_current_user,
            use_case=mock_use_case,
        )

        # Assert
        assert response.data is not None
        # Default privacy flags should be applied
        assert response.data.privacy_flags["show_online"] is True
        assert response.data.privacy_flags["allow_stranger_chat"] is True

    @pytest.mark.asyncio
    async def test_get_my_profile_with_empty_preferences(self, mock_current_user):
        """Test profile with None preferences gets empty dict"""
        # Arrange
        profile_no_prefs = Profile(
            id=uuid4(),
            user_id=mock_current_user,
            nickname="TestUser",
            avatar_url=None,
            bio=None,
            region="US",
            preferences=None,  # None preferences
            privacy_flags={"show_online": False},
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = profile_no_prefs

        # Act
        response = await get_my_profile(
            current_user_id=mock_current_user,
            use_case=mock_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.preferences == {}


class TestUpdateMyProfile:
    """Tests for PUT /profile/me endpoint"""

    @pytest.fixture
    def mock_current_user(self):
        """Mock authenticated user ID"""
        return uuid4()

    @pytest.fixture
    def sample_updated_profile(self, mock_current_user):
        """Sample updated profile entity"""
        return Profile(
            id=uuid4(),
            user_id=mock_current_user,
            nickname="UpdatedUser",
            avatar_url="https://example.com/new_avatar.jpg",
            bio="Updated bio",
            region="JP",
            preferences={"lang": "ja-JP", "theme": "dark"},
            privacy_flags={"show_online": False, "allow_stranger_chat": False, "nearby_visible": False},
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 3, 15, 30, 0),
        )

    @pytest.mark.asyncio
    async def test_update_my_profile_success(self, mock_current_user, sample_updated_profile):
        """Test successful profile update"""
        # Arrange
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = sample_updated_profile

        request = UpdateProfileRequest(
            nickname="UpdatedUser",
            avatar_url="https://example.com/new_avatar.jpg",
            bio="Updated bio",
            region="JP",
            preferences={"lang": "ja-JP", "theme": "dark"},
            privacy_flags={
                "show_online": False,
                "allow_stranger_chat": False,
                "nearby_visible": False,
            },
        )

        # Act
        response = await update_my_profile(
            request=request,
            current_user_id=mock_current_user,
            use_case=mock_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.nickname == "UpdatedUser"
        assert response.data.avatar_url == "https://example.com/new_avatar.jpg"
        assert response.data.bio == "Updated bio"
        assert response.data.region == "JP"
        assert response.data.preferences["lang"] == "ja-JP"
        assert response.data.preferences["theme"] == "dark"
        assert response.data.privacy_flags["show_online"] is False
        assert response.data.privacy_flags["allow_stranger_chat"] is False
        assert response.error is None
        
        # Verify use case was called correctly
        mock_use_case.execute.assert_called_once()
        call_kwargs = mock_use_case.execute.call_args.kwargs
        assert call_kwargs["user_id"] == mock_current_user
        assert call_kwargs["nickname"] == "UpdatedUser"
        assert call_kwargs["bio"] == "Updated bio"
        assert call_kwargs["region"] == "JP"

    @pytest.mark.asyncio
    async def test_update_my_profile_partial_update(self, mock_current_user):
        """Test partial profile update (only nickname)"""
        # Arrange
        updated_profile = Profile(
            id=uuid4(),
            user_id=mock_current_user,
            nickname="NewNickname",
            avatar_url="https://example.com/avatar.jpg",
            bio="Original bio",
            region="TW",
            preferences={"lang": "zh-TW"},
            privacy_flags={"show_online": True, "allow_stranger_chat": True},
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 3),
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = updated_profile

        request = UpdateProfileRequest(nickname="NewNickname")

        # Act
        response = await update_my_profile(
            request=request,
            current_user_id=mock_current_user,
            use_case=mock_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.nickname == "NewNickname"

    @pytest.mark.asyncio
    async def test_update_my_profile_failed(self, mock_current_user):
        """Test profile update failure raises HTTPException"""
        # Arrange
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = None

        request = UpdateProfileRequest(nickname="NewNickname")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_my_profile(
                request=request,
                current_user_id=mock_current_user,
                use_case=mock_use_case,
            )
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "INTERNAL_ERROR" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_my_profile_with_privacy_flags_only(self, mock_current_user):
        """Test updating only privacy flags"""
        # Arrange
        updated_profile = Profile(
            id=uuid4(),
            user_id=mock_current_user,
            nickname="TestUser",
            avatar_url="https://example.com/avatar.jpg",
            bio="Bio",
            region="TW",
            preferences={},
            privacy_flags={"show_online": False, "allow_stranger_chat": True, "nearby_visible": False},
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 3),
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = updated_profile

        request = UpdateProfileRequest(
            privacy_flags={
                "show_online": False,
                "allow_stranger_chat": True,
                "nearby_visible": False,
            }
        )

        # Act
        response = await update_my_profile(
            request=request,
            current_user_id=mock_current_user,
            use_case=mock_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.privacy_flags["show_online"] is False
        assert response.data.privacy_flags["allow_stranger_chat"] is True
        assert response.data.privacy_flags["nearby_visible"] is False

    @pytest.mark.asyncio
    async def test_update_my_profile_clear_optional_fields(self, mock_current_user):
        """Test clearing optional fields (avatar_url, bio)"""
        # Arrange
        updated_profile = Profile(
            id=uuid4(),
            user_id=mock_current_user,
            nickname="TestUser",
            avatar_url=None,  # Cleared
            bio=None,  # Cleared
            region="TW",
            preferences={},
            privacy_flags={"show_online": True, "allow_stranger_chat": True},
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 3),
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = updated_profile

        request = UpdateProfileRequest(avatar_url=None, bio=None)

        # Act
        response = await update_my_profile(
            request=request,
            current_user_id=mock_current_user,
            use_case=mock_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.avatar_url is None
        assert response.data.bio is None

    @pytest.mark.asyncio
    async def test_update_my_profile_with_complex_preferences(self, mock_current_user):
        """Test updating with complex preferences dict"""
        # Arrange
        complex_prefs = {
            "lang": "en-US",
            "theme": "dark",
            "notifications": {"email": True, "push": False},
            "display": {"density": "comfortable", "items_per_page": 20},
        }
        
        updated_profile = Profile(
            id=uuid4(),
            user_id=mock_current_user,
            nickname="TestUser",
            avatar_url="https://example.com/avatar.jpg",
            bio="Bio",
            region="US",
            preferences=complex_prefs,
            privacy_flags={"show_online": True, "allow_stranger_chat": True},
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 3),
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = updated_profile

        request = UpdateProfileRequest(preferences=complex_prefs)

        # Act
        response = await update_my_profile(
            request=request,
            current_user_id=mock_current_user,
            use_case=mock_use_case,
        )

        # Assert
        assert response.data is not None
        assert response.data.preferences == complex_prefs
        assert response.data.preferences["notifications"]["email"] is True
        assert response.data.preferences["display"]["items_per_page"] == 20
