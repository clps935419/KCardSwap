"""Integration tests for city list API."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


class TestCityListAPI:
    """Integration tests for GET /api/v1/locations/cities endpoint."""
    
    def test_get_all_cities_success(self, test_client):
        """Test successfully retrieving all cities without authentication."""
        # Act
        response = test_client.get("/api/v1/locations/cities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "cities" in data
        assert isinstance(data["cities"], list)
        
        # Check we have all 22 Taiwan cities
        assert len(data["cities"]) == 22
        
        # Check first city structure
        first_city = data["cities"][0]
        assert "code" in first_city
        assert "name" in first_city
        assert "name_zh" in first_city
    
    def test_get_all_cities_contains_six_municipalities(self, test_client):
        """Test that response includes all six special municipalities."""
        # Act
        response = test_client.get("/api/v1/locations/cities")
        
        # Assert
        assert response.status_code == 200
        cities = response.json()["cities"]
        
        # Six special municipalities
        municipality_codes = ["TPE", "NTP", "TAO", "TXG", "TNN", "KHH"]
        city_codes = [city["code"] for city in cities]
        
        for code in municipality_codes:
            assert code in city_codes, f"Municipality {code} not found in response"
    
    def test_get_all_cities_has_correct_field_types(self, test_client):
        """Test that all cities have correct field types."""
        # Act
        response = test_client.get("/api/v1/locations/cities")
        
        # Assert
        assert response.status_code == 200
        cities = response.json()["cities"]
        
        for city in cities:
            assert isinstance(city["code"], str), f"City code should be string"
            assert isinstance(city["name"], str), f"City name should be string"
            assert isinstance(city["name_zh"], str), f"City name_zh should be string"
            assert len(city["code"]) == 3, f"City code should be 3 characters"
    
    def test_get_all_cities_includes_taipei(self, test_client):
        """Test that Taipei City is included with correct data."""
        # Act
        response = test_client.get("/api/v1/locations/cities")
        
        # Assert
        assert response.status_code == 200
        cities = response.json()["cities"]
        
        taipei = next((c for c in cities if c["code"] == "TPE"), None)
        assert taipei is not None, "Taipei not found in cities"
        assert taipei["name"] == "Taipei City"
        assert taipei["name_zh"] == "台北市"
    
    def test_get_all_cities_no_authentication_required(self, test_client):
        """Test that endpoint is publicly accessible without JWT token."""
        # Act - no Authorization header
        response = test_client.get("/api/v1/locations/cities")
        
        # Assert - should succeed without authentication
        assert response.status_code == 200
        assert "cities" in response.json()
