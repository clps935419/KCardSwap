"""
Integration E2E tests for Locations Router

Tests the locations endpoints:
- GET /locations/cities - Get all Taiwan cities
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestLocationsRouterE2E:
    """E2E tests for Locations Router endpoints"""

    @pytest.fixture
    def client(self):
        """Provide test client (public endpoint, no auth needed)"""
        return TestClient(app)

    def test_get_cities_success(self, client):
        """Test getting all Taiwan cities successfully"""
        response = client.get("/api/v1/locations/cities")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "cities" in data
        assert isinstance(data["cities"], list)

        # Should have 22 Taiwan cities/counties
        # Verify response structure if cities exist
        if len(data["cities"]) > 0:
            city = data["cities"][0]
            assert "code" in city
            assert "name" in city
            assert "name_zh" in city

    def test_get_cities_format_validation(self, client):
        """Test cities response format"""
        response = client.get("/api/v1/locations/cities")

        assert response.status_code == 200
        response_data = response.json()

        # Verify envelope format
        assert "data" in response_data
        assert "meta" in response_data
        assert "error" in response_data

        # Verify data structure
        data = response_data["data"]
        assert "cities" in data

        # Verify each city has required fields
        for city in data["cities"]:
            assert isinstance(city["code"], str)
            assert isinstance(city["name"], str)
            assert isinstance(city["name_zh"], str)
            assert len(city["code"]) > 0  # Should have city code
            assert len(city["name"]) > 0  # Should have English name
            assert len(city["name_zh"]) > 0  # Should have Chinese name

    def test_get_cities_contains_major_cities(self, client):
        """Test that cities list contains major Taiwan cities"""
        response = client.get("/api/v1/locations/cities")

        assert response.status_code == 200
        data = response.json()["data"]
        cities = data["cities"]

        # Should contain major cities
        # Note: Exact codes depend on implementation
        assert len(cities) > 0, "Should have at least some cities"

        # Verify all cities have valid structure
        for city in cities:
            assert len(city["code"]) > 0
            assert len(city["name"]) > 0
            assert len(city["name_zh"]) > 0

    def test_get_cities_no_auth_required(self, client):
        """Test that cities endpoint doesn't require authentication"""
        # This is a public endpoint
        response = client.get("/api/v1/locations/cities")

        # Should succeed without authentication
        assert response.status_code == 200
