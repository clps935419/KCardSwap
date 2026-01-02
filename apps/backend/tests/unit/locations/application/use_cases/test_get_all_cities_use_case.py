"""
Unit tests for GetAllCitiesUseCase

Tests the get all cities use case with mocked dependencies.
"""

from unittest.mock import AsyncMock

import pytest

from app.modules.locations.application.use_cases.get_all_cities_use_case import (
    GetAllCitiesUseCase,
)
from app.modules.locations.domain.value_objects.city import City
from app.modules.posts.domain.entities.city_code import CityCode


class TestGetAllCitiesUseCase:
    """Test GetAllCitiesUseCase"""

    @pytest.fixture
    def mock_city_repository(self):
        """Create mock city repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_city_repository):
        """Create use case instance"""
        return GetAllCitiesUseCase(city_repository=mock_city_repository)

    @pytest.fixture
    def sample_cities(self):
        """Create sample cities list"""
        return [
            City(CityCode.TPE, "Taipei City", "台北市"),
            City(CityCode.NTP, "New Taipei City", "新北市"),
            City(CityCode.TAO, "Taoyuan City", "桃園市"),
            City(CityCode.TXG, "Taichung City", "台中市"),
            City(CityCode.TNN, "Tainan City", "台南市"),
            City(CityCode.KHH, "Kaohsiung City", "高雄市"),
        ]

    @pytest.mark.asyncio
    async def test_get_all_cities_success(
        self, use_case, mock_city_repository, sample_cities
    ):
        """Test successful retrieval of all cities"""
        # Arrange
        mock_city_repository.get_all_cities.return_value = sample_cities

        # Act
        result = await use_case.execute()

        # Assert
        assert result is not None
        assert len(result) == 6
        assert result[0].code == CityCode.TPE
        assert result[0].name == "Taipei City"
        assert result[0].name_zh == "台北市"
        mock_city_repository.get_all_cities.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_cities_empty(self, use_case, mock_city_repository):
        """Test retrieval when no cities are available"""
        # Arrange
        mock_city_repository.get_all_cities.return_value = []

        # Act
        result = await use_case.execute()

        # Assert
        assert result is not None
        assert len(result) == 0
        mock_city_repository.get_all_cities.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_cities_returns_list(
        self, use_case, mock_city_repository, sample_cities
    ):
        """Test that result is always a list"""
        # Arrange
        mock_city_repository.get_all_cities.return_value = sample_cities

        # Act
        result = await use_case.execute()

        # Assert
        assert isinstance(result, list)
        for city in result:
            assert isinstance(city, City)
