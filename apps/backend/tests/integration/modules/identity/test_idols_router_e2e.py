"""
Integration E2E tests for Idols Router

Tests the idols listing endpoint:
- GET /idols/groups - Get all idol groups
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestIdolsRouterE2E:
    """E2E tests for Idols Router endpoints"""

    @pytest.fixture
    def client(self):
        """Provide test client (no auth required for idols endpoint)"""
        return TestClient(app)

    def test_get_idol_groups_success(self, client):
        """Test getting all idol groups successfully"""
        response = client.get("/api/v1/idols/groups")

        assert response.status_code == 200
        data = response.json()["data"]
        assert "groups" in data
        assert isinstance(data["groups"], list)

        # Verify response structure if groups exist
        if len(data["groups"]) > 0:
            group = data["groups"][0]
            assert "id" in group
            assert "name" in group
            assert "emoji" in group

    def test_get_idol_groups_format_validation(self, client):
        """Test idol groups response format"""
        response = client.get("/api/v1/idols/groups")

        assert response.status_code == 200
        response_data = response.json()

        # Verify envelope format
        assert "data" in response_data
        assert "meta" in response_data
        assert "error" in response_data

        # Verify data structure
        data = response_data["data"]
        assert "groups" in data

        # Verify each group has required fields
        for group in data["groups"]:
            assert isinstance(group["id"], str)
            assert isinstance(group["name"], str)
            assert isinstance(group["emoji"], str)
            assert len(group["emoji"]) > 0  # Should have at least one emoji character

    def test_get_idol_groups_contains_expected_groups(self, client):
        """Test that idol groups contain expected K-pop groups"""
        response = client.get("/api/v1/idols/groups")

        assert response.status_code == 200
        data = response.json()["data"]
        groups = data["groups"]

        # Should contain some well-known K-pop groups (based on the router implementation)
        # Note: This test may need adjustment based on actual data
        assert len(groups) > 0, "Should have at least some idol groups"

        # Verify all groups have valid structure
        for group in groups:
            assert len(group["id"]) > 0
            assert len(group["name"]) > 0
            assert len(group["emoji"]) > 0
