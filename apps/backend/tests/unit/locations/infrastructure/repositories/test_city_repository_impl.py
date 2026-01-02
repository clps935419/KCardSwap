"""
Unit tests for CityRepositoryImpl

Tests the city repository implementation.
"""

import pytest

from app.modules.locations.domain.value_objects.city import City
from app.modules.locations.infrastructure.repositories.city_repository_impl import (
    CityRepositoryImpl,
)
from app.modules.posts.domain.entities.city_code import CityCode


class TestCityRepositoryImpl:
    """Test CityRepositoryImpl"""

    @pytest.fixture
    def repository(self):
        """Create repository instance"""
        return CityRepositoryImpl()

    @pytest.mark.asyncio
    async def test_get_all_cities_returns_22_cities(self, repository):
        """Test that repository returns all 22 Taiwan cities"""
        # Act
        result = await repository.get_all_cities()

        # Assert
        assert len(result) == 22
        assert all(isinstance(city, City) for city in result)

    @pytest.mark.asyncio
    async def test_get_all_cities_includes_taipei(self, repository):
        """Test that Taipei City is included"""
        # Act
        result = await repository.get_all_cities()

        # Assert
        taipei = next((c for c in result if c.code == CityCode.TPE), None)
        assert taipei is not None
        assert taipei.name == "Taipei City"
        assert taipei.name_zh == "台北市"

    @pytest.mark.asyncio
    async def test_get_all_cities_includes_special_municipalities(self, repository):
        """Test that all 6 special municipalities are included"""
        # Act
        result = await repository.get_all_cities()

        # Assert
        special_municipalities = [
            CityCode.TPE,  # Taipei
            CityCode.NTP,  # New Taipei
            CityCode.TAO,  # Taoyuan
            CityCode.TXG,  # Taichung
            CityCode.TNN,  # Tainan
            CityCode.KHH,  # Kaohsiung
        ]

        for code in special_municipalities:
            city = next((c for c in result if c.code == code), None)
            assert city is not None, f"Special municipality {code} not found"

    @pytest.mark.asyncio
    async def test_get_all_cities_includes_provincial_cities(self, repository):
        """Test that provincial cities are included"""
        # Act
        result = await repository.get_all_cities()

        # Assert
        provincial_cities = [
            CityCode.HSZ,  # Hsinchu City
            CityCode.CYI,  # Chiayi City
        ]

        for code in provincial_cities:
            city = next((c for c in result if c.code == code), None)
            assert city is not None, f"Provincial city {code} not found"

    @pytest.mark.asyncio
    async def test_get_all_cities_includes_counties(self, repository):
        """Test that counties are included"""
        # Act
        result = await repository.get_all_cities()

        # Assert
        # Check a few representative counties
        counties = [
            CityCode.MIA,  # Miaoli County
            CityCode.NAN,  # Nantou County
            CityCode.ILA,  # Yilan County
            CityCode.PEN,  # Penghu County
            CityCode.KIN,  # Kinmen County
        ]

        for code in counties:
            city = next((c for c in result if c.code == code), None)
            assert city is not None, f"County {code} not found"

    @pytest.mark.asyncio
    async def test_get_all_cities_returns_copy(self, repository):
        """Test that repository returns a copy, not the original list"""
        # Act
        result1 = await repository.get_all_cities()
        result2 = await repository.get_all_cities()

        # Assert
        assert result1 is not result2  # Different list objects
        assert result1 == result2  # But same content

    @pytest.mark.asyncio
    async def test_cities_have_all_required_fields(self, repository):
        """Test that all cities have code, name, and name_zh"""
        # Act
        result = await repository.get_all_cities()

        # Assert
        for city in result:
            assert city.code is not None
            assert city.name is not None
            assert city.name_zh is not None
            assert len(city.name) > 0
            assert len(city.name_zh) > 0
