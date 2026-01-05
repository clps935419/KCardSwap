"""
Unit tests for UpdateUserLocationUseCase
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.social.application.use_cases.nearby.update_user_location_use_case import (
    UpdateUserLocationUseCase,
)


class TestUpdateUserLocationUseCase:
    """Test UpdateUserLocationUseCase"""

    @pytest.fixture
    def mock_profile_service(self):
        """Create mock profile repository"""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def use_case(self, mock_profile_service):
        """Create use case instance"""
        return UpdateUserLocationUseCase(profile_service=mock_profile_service)

    @pytest.fixture
    def mock_profile(self):
        """Create mock profile"""
        profile = Mock()
        profile.user_id = uuid4()
        profile.nickname = "TestUser"
        profile.last_lat = None
        profile.last_lng = None
        profile.update_location = Mock()
        return profile

    @pytest.mark.asyncio
    async def test_update_user_location_success(
        self, use_case, mock_profile_service, mock_profile
    ):
        """Test successful location update"""
        # Arrange
        user_id = uuid4()
        lat = 25.0330
        lng = 121.5654

        # Service returns True for successful update
        mock_profile_service.update_user_location.return_value = True

        # Act
        result = await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        # Assert
        assert result is None  # execute() returns None on success
        mock_profile_service.update_user_location.assert_called_once_with(
            user_id, lat, lng
        )

    @pytest.mark.asyncio
    async def test_update_user_location_valid_coordinates(
        self, use_case, mock_profile_service, mock_profile
    ):
        """Test with various valid coordinates"""
        # Arrange
        user_id = uuid4()
        mock_profile_service.update_user_location.return_value = True

        # Test cases: (lat, lng)
        test_cases = [
            (0.0, 0.0),  # Null Island
            (90.0, 180.0),  # Max positive
            (-90.0, -180.0),  # Max negative
            (25.0330, 121.5654),  # Taipei
            (-33.8688, 151.2093),  # Sydney
            (51.5074, -0.1278),  # London
        ]

        for lat, lng in test_cases:
            mock_profile.update_location.reset_mock()

            # Act
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

            # Assert
            mock_profile.update_location.assert_called_once_with(lat, lng)

    @pytest.mark.asyncio
    async def test_update_user_location_invalid_latitude_too_low(self, use_case):
        """Test invalid latitude below -90"""
        # Arrange
        user_id = uuid4()
        lat = -91.0
        lng = 121.5654

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        assert "Latitude must be between -90 and 90" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_location_invalid_latitude_too_high(self, use_case):
        """Test invalid latitude above 90"""
        # Arrange
        user_id = uuid4()
        lat = 91.0
        lng = 121.5654

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        assert "Latitude must be between -90 and 90" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_location_invalid_longitude_too_low(self, use_case):
        """Test invalid longitude below -180"""
        # Arrange
        user_id = uuid4()
        lat = 25.0330
        lng = -181.0

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        assert "Longitude must be between -180 and 180" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_location_invalid_longitude_too_high(self, use_case):
        """Test invalid longitude above 180"""
        # Arrange
        user_id = uuid4()
        lat = 25.0330
        lng = 181.0

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        assert "Longitude must be between -180 and 180" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_location_profile_not_found(
        self, use_case, mock_profile_service
    ):
        """Test exception when profile not found"""
        # Arrange
        user_id = uuid4()
        lat = 25.0330
        lng = 121.5654

        # Service returns False for failed update
        mock_profile_service.update_user_location.return_value = False

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        assert "Failed to update location" in str(exc_info.value)
        assert str(user_id) in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_location_validation_before_repository_call(
        self, use_case, mock_profile_service
    ):
        """Test that validation happens before repository is accessed"""
        # Arrange
        user_id = uuid4()
        lat = 91.0  # Invalid
        lng = 121.5654

        # Act & Assert
        with pytest.raises(ValueError):
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        # Service should NOT be called when validation fails
        mock_profile_service.update_user_location.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_location_save_called_after_update(
        self, use_case, mock_profile_service, mock_profile
    ):
        """Test that save is called after update_location"""
        # Arrange
        user_id = uuid4()
        lat = 25.0330
        lng = 121.5654

        mock_profile_service.update_user_location.return_value = True
        # Removed

        # Track call order
        call_order = []
        mock_profile.update_location.side_effect = lambda *args: call_order.append(
            "update"
        )
        mock_profile_service.side_effect = lambda *args: call_order.append(
            "save"
        )

        # Act
        await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        # Assert - update_location should be called before save
        assert call_order == ["update", "save"]

    @pytest.mark.asyncio
    async def test_update_user_location_multiple_updates_same_user(
        self, use_case, mock_profile_service, mock_profile
    ):
        """Test multiple location updates for the same user"""
        # Arrange
        user_id = uuid4()
        mock_profile_service.update_user_location.return_value = True
        # Removed

        locations = [
            (25.0330, 121.5654),  # Taipei
            (25.0340, 121.5660),  # Move slightly
            (25.0350, 121.5670),  # Move again
        ]

        # Act & Assert
        for lat, lng in locations:
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)
            mock_profile.update_location.assert_called_with(lat, lng)

        # Verify repository was called for each update
        assert mock_profile_service.update_user_location.call_count == 3
        assert mock_profile_service.save.call_count == 3

    @pytest.mark.asyncio
    async def test_update_user_location_edge_cases(
        self, use_case, mock_profile_service, mock_profile
    ):
        """Test edge cases for coordinate boundaries"""
        # Arrange
        user_id = uuid4()
        mock_profile_service.update_user_location.return_value = True
        # Removed

        # Test exact boundary values
        boundary_cases = [
            (90.0, 180.0),  # Max positive boundaries
            (-90.0, -180.0),  # Max negative boundaries
            (90.0, -180.0),  # Mixed boundaries
            (-90.0, 180.0),  # Mixed boundaries
        ]

        for lat, lng in boundary_cases:
            mock_profile.update_location.reset_mock()

            # Act
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

            # Assert
            mock_profile.update_location.assert_called_once_with(lat, lng)

    @pytest.mark.asyncio
    async def test_update_user_location_profile_with_existing_location(
        self, use_case, mock_profile_service
    ):
        """Test updating location when profile already has a location"""
        # Arrange
        user_id = uuid4()
        profile = Mock()
        profile.user_id = user_id
        profile.last_lat = 24.0
        profile.last_lng = 120.0
        profile.update_location = Mock()

        mock_profile_service.update_user_location.return_value = profile
        mock_profile_service.return_value = profile

        # Act
        new_lat = 25.0330
        new_lng = 121.5654
        await use_case.execute(user_id=user_id, lat=new_lat, lng=new_lng)

        # Assert - should update to new location
        profile.update_location.assert_called_once_with(new_lat, new_lng)
        mock_profile_service.assert_called_once_with(profile)

    @pytest.mark.asyncio
    async def test_update_user_location_zero_coordinates(
        self, use_case, mock_profile_service, mock_profile
    ):
        """Test updating with zero coordinates (valid case: Null Island)"""
        # Arrange
        user_id = uuid4()
        mock_profile_service.update_user_location.return_value = True
        # Removed

        # Act
        await use_case.execute(user_id=user_id, lat=0.0, lng=0.0)

        # Assert
        mock_profile.update_location.assert_called_once_with(0.0, 0.0)

    @pytest.mark.asyncio
    async def test_update_user_location_float_precision(
        self, use_case, mock_profile_service, mock_profile
    ):
        """Test with high-precision floating point coordinates"""
        # Arrange
        user_id = uuid4()
        mock_profile_service.update_user_location.return_value = True
        # Removed

        # High precision coordinates
        lat = 25.033012345678
        lng = 121.565412345678

        # Act
        await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        # Assert - should preserve precision
        mock_profile.update_location.assert_called_once_with(lat, lng)

    @pytest.mark.asyncio
    async def test_update_user_location_both_coordinates_invalid(self, use_case):
        """Test when both coordinates are invalid"""
        # Arrange
        user_id = uuid4()
        lat = 91.0  # Invalid
        lng = 181.0  # Invalid

        # Act & Assert - latitude is checked first
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(user_id=user_id, lat=lat, lng=lng)

        assert "Latitude must be between -90 and 90" in str(exc_info.value)
