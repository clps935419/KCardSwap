"""
Unit tests for Location Router

Tests the location router endpoints:
- GET /locations/cities - Get all Taiwan cities
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest


class TestLocationRouter:
    """Test cases for Location Router endpoints"""

    @pytest.fixture
    def mock_city_entity(self):
        """Mock city entity"""
        mock_city = MagicMock()
        mock_city.code = MagicMock()
        mock_city.code.value = "TPE"
        mock_city.name = "Taipei City"
        mock_city.name_zh = "台北市"
        return mock_city

    @pytest.fixture
    def mock_cities_list(self):
        """Mock list of cities"""
        cities = []
        
        # Taipei City
        city1 = MagicMock()
        city1.code = MagicMock()
        city1.code.value = "TPE"
        city1.name = "Taipei City"
        city1.name_zh = "台北市"
        cities.append(city1)
        
        # New Taipei City
        city2 = MagicMock()
        city2.code = MagicMock()
        city2.code.value = "NTP"
        city2.name = "New Taipei City"
        city2.name_zh = "新北市"
        cities.append(city2)
        
        # Taoyuan City
        city3 = MagicMock()
        city3.code = MagicMock()
        city3.code.value = "TAO"
        city3.name = "Taoyuan City"
        city3.name_zh = "桃園市"
        cities.append(city3)
        
        return cities

    @pytest.fixture
    def mock_use_case(self):
        """Mock get all cities use case"""
        return AsyncMock()

    @pytest.fixture
    def mock_container(self):
        """Mock dependency injection container"""
        return MagicMock()

    # Get Cities Tests

    @pytest.mark.asyncio
    async def test_get_cities_success(
        self, mock_use_case, mock_container, mock_cities_list
    ):
        """Test successfully retrieving all Taiwan cities"""
        # Arrange
        from app.modules.locations.presentation.routers.location_router import get_cities

        mock_container.get.return_value = mock_use_case
        mock_use_case.execute.return_value = mock_cities_list

        # Act
        result = await get_cities(container=mock_container)

        # Assert
        assert result.data.cities is not None
        assert len(result.data.cities) == 3
        assert result.data.cities[0].code == "TPE"
        assert result.data.cities[0].name == "Taipei City"
        assert result.data.cities[0].name_zh == "台北市"
        assert result.data.cities[1].code == "NTP"
        assert result.data.cities[2].code == "TAO"
        assert result.error is None
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cities_single_city(
        self, mock_use_case, mock_container, mock_city_entity
    ):
        """Test retrieving a single city"""
        # Arrange
        from app.modules.locations.presentation.routers.location_router import get_cities

        mock_container.get.return_value = mock_use_case
        mock_use_case.execute.return_value = [mock_city_entity]

        # Act
        result = await get_cities(container=mock_container)

        # Assert
        assert len(result.data.cities) == 1
        assert result.data.cities[0].code == "TPE"
        assert result.data.cities[0].name == "Taipei City"
        assert result.data.cities[0].name_zh == "台北市"

    @pytest.mark.asyncio
    async def test_get_cities_empty_list(self, mock_use_case, mock_container):
        """Test retrieving cities when no cities exist (edge case)"""
        # Arrange
        from app.modules.locations.presentation.routers.location_router import get_cities

        mock_container.get.return_value = mock_use_case
        mock_use_case.execute.return_value = []

        # Act
        result = await get_cities(container=mock_container)

        # Assert
        assert len(result.data.cities) == 0
        assert result.error is None

    @pytest.mark.asyncio
    async def test_get_cities_all_22_cities(self, mock_use_case, mock_container):
        """Test retrieving all 22 Taiwan cities/counties"""
        # Arrange
        from app.modules.locations.presentation.routers.location_router import get_cities

        # Create all 22 Taiwan cities
        all_cities = []
        city_data = [
            ("TPE", "Taipei City", "台北市"),
            ("NTP", "New Taipei City", "新北市"),
            ("TAO", "Taoyuan City", "桃園市"),
            ("TCH", "Taichung City", "台中市"),
            ("TNN", "Tainan City", "台南市"),
            ("KHH", "Kaohsiung City", "高雄市"),
            ("HSC", "Hsinchu City", "新竹市"),
            ("HSZ", "Hsinchu County", "新竹縣"),
            ("MIA", "Miaoli County", "苗栗縣"),
            ("CHA", "Changhua County", "彰化縣"),
            ("NAN", "Nantou County", "南投縣"),
            ("YUN", "Yunlin County", "雲林縣"),
            ("CYI", "Chiayi City", "嘉義市"),
            ("CYQ", "Chiayi County", "嘉義縣"),
            ("PIF", "Pingtung County", "屏東縣"),
            ("ILA", "Yilan County", "宜蘭縣"),
            ("HUA", "Hualien County", "花蓮縣"),
            ("TTT", "Taitung County", "台東縣"),
            ("PEN", "Penghu County", "澎湖縣"),
            ("KIN", "Kinmen County", "金門縣"),
            ("LIE", "Lienchiang County", "連江縣"),
            ("KEE", "Keelung City", "基隆市"),
        ]

        for code, name, name_zh in city_data:
            city = MagicMock()
            city.code = MagicMock()
            city.code.value = code
            city.name = name
            city.name_zh = name_zh
            all_cities.append(city)

        mock_container.get.return_value = mock_use_case
        mock_use_case.execute.return_value = all_cities

        # Act
        result = await get_cities(container=mock_container)

        # Assert
        assert len(result.data.cities) == 22
        assert result.data.cities[0].code == "TPE"
        assert result.data.cities[5].code == "KHH"  # Kaohsiung
        assert result.data.cities[21].code == "KEE"  # Keelung

    @pytest.mark.asyncio
    async def test_get_cities_response_structure(
        self, mock_use_case, mock_container, mock_cities_list
    ):
        """Test that response has correct structure with data/meta/error envelope"""
        # Arrange
        from app.modules.locations.presentation.routers.location_router import get_cities

        mock_container.get.return_value = mock_use_case
        mock_use_case.execute.return_value = mock_cities_list

        # Act
        result = await get_cities(container=mock_container)

        # Assert
        assert hasattr(result, "data")
        assert hasattr(result, "meta")
        assert hasattr(result, "error")
        assert result.meta is None
        assert result.error is None
        assert hasattr(result.data, "cities")

    @pytest.mark.asyncio
    async def test_get_cities_uses_dependency_injection(
        self, mock_use_case, mock_container, mock_cities_list
    ):
        """Test that endpoint properly uses dependency injection container"""
        # Arrange
        from app.modules.locations.presentation.routers.location_router import get_cities
        from app.modules.locations.application.use_cases.get_all_cities_use_case import (
            GetAllCitiesUseCase,
        )

        mock_container.get.return_value = mock_use_case
        mock_use_case.execute.return_value = mock_cities_list

        # Act
        await get_cities(container=mock_container)

        # Assert
        mock_container.get.assert_called_once_with(GetAllCitiesUseCase)

    @pytest.mark.asyncio
    async def test_get_cities_calls_use_case_execute(
        self, mock_use_case, mock_container, mock_cities_list
    ):
        """Test that endpoint calls use case execute method"""
        # Arrange
        from app.modules.locations.presentation.routers.location_router import get_cities

        mock_container.get.return_value = mock_use_case
        mock_use_case.execute.return_value = mock_cities_list

        # Act
        await get_cities(container=mock_container)

        # Assert
        mock_use_case.execute.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_get_cities_city_response_fields(
        self, mock_use_case, mock_container, mock_city_entity
    ):
        """Test that each city response has all required fields"""
        # Arrange
        from app.modules.locations.presentation.routers.location_router import get_cities

        mock_container.get.return_value = mock_use_case
        mock_use_case.execute.return_value = [mock_city_entity]

        # Act
        result = await get_cities(container=mock_container)

        # Assert
        city = result.data.cities[0]
        assert hasattr(city, "code")
        assert hasattr(city, "name")
        assert hasattr(city, "name_zh")
        assert city.code is not None
        assert city.name is not None
        assert city.name_zh is not None
