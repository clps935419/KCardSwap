"""Integration tests for idol groups list API."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create test client."""
    from app.main import app

    return TestClient(app)


class TestIdolGroupsListAPI:
    """Integration tests for GET /api/v1/idols/groups endpoint."""

    def test_get_all_idol_groups_success(self, test_client):
        """Test successfully retrieving all idol groups without authentication."""
        # Act
        response = test_client.get("/api/v1/idols/groups")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check response structure (using standardized envelope)
        assert "data" in data
        assert "groups" in data["data"]
        assert isinstance(data["data"]["groups"], list)

        # Check we have all 12 idol groups
        assert len(data["data"]["groups"]) == 12

        # Check first group structure
        first_group = data["data"]["groups"][0]
        assert "id" in first_group
        assert "name" in first_group
        assert "emoji" in first_group

    def test_get_all_idol_groups_contains_key_groups(self, test_client):
        """Test that response includes key idol groups."""
        # Act
        response = test_client.get("/api/v1/idols/groups")

        # Assert
        assert response.status_code == 200
        groups = response.json()["data"]["groups"]

        # Key idol groups that should be present
        expected_groups = ["newjeans", "ive", "aespa", "blackpink", "bts"]
        group_ids = [group["id"] for group in groups]

        for group_id in expected_groups:
            assert (
                group_id in group_ids
            ), f"Idol group {group_id} not found in response"

    def test_get_all_idol_groups_has_correct_field_types(self, test_client):
        """Test that all idol groups have correct field types."""
        # Act
        response = test_client.get("/api/v1/idols/groups")

        # Assert
        assert response.status_code == 200
        groups = response.json()["data"]["groups"]

        for group in groups:
            assert isinstance(group["id"], str), "Group id should be string"
            assert isinstance(group["name"], str), "Group name should be string"
            assert isinstance(group["emoji"], str), "Group emoji should be string"
            assert len(group["id"]) > 0, "Group id should not be empty"
            assert len(group["name"]) > 0, "Group name should not be empty"
            assert len(group["emoji"]) > 0, "Group emoji should not be empty"

    def test_get_all_idol_groups_includes_newjeans(self, test_client):
        """Test that NewJeans is included with correct data."""
        # Act
        response = test_client.get("/api/v1/idols/groups")

        # Assert
        assert response.status_code == 200
        groups = response.json()["data"]["groups"]

        newjeans = next((g for g in groups if g["id"] == "newjeans"), None)
        assert newjeans is not None, "NewJeans not found in idol groups"
        assert newjeans["name"] == "NewJeans"
        assert newjeans["emoji"] == "👖"

    def test_get_all_idol_groups_no_authentication_required(self, test_client):
        """Test that endpoint is publicly accessible without JWT token."""
        # Act - no Authorization header
        response = test_client.get("/api/v1/idols/groups")

        # Assert - should succeed without authentication
        assert response.status_code == 200
        assert "data" in response.json()
        assert "groups" in response.json()["data"]

    def test_idol_groups_are_sorted_consistently(self, test_client):
        """Test that idol groups are returned in a consistent order."""
        # Act - call endpoint multiple times
        response1 = test_client.get("/api/v1/idols/groups")
        response2 = test_client.get("/api/v1/idols/groups")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        groups1 = response1.json()["data"]["groups"]
        groups2 = response2.json()["data"]["groups"]

        # Groups should be in the same order
        group_ids_1 = [g["id"] for g in groups1]
        group_ids_2 = [g["id"] for g in groups2]
        assert (
            group_ids_1 == group_ids_2
        ), "Idol groups should be returned in consistent order"

    def test_idol_groups_aligned_with_mobile_constants(self, test_client):
        """Test that backend groups match mobile app constants."""
        # Act
        response = test_client.get("/api/v1/idols/groups")

        # Assert
        assert response.status_code == 200
        groups = response.json()["data"]["groups"]

        # Expected groups from mobile: apps/mobile/src/features/profile/constants/idolGroups.ts
        expected_mobile_groups = [
            {"id": "newjeans", "name": "NewJeans", "emoji": "👖"},
            {"id": "ive", "name": "IVE", "emoji": "🦢"},
            {"id": "aespa", "name": "aespa", "emoji": "🦋"},
            {"id": "le-sserafim", "name": "LE SSERAFIM", "emoji": "🌸"},
            {"id": "blackpink", "name": "BLACKPINK", "emoji": "💖"},
            {"id": "twice", "name": "TWICE", "emoji": "🍭"},
            {"id": "seventeen", "name": "SEVENTEEN", "emoji": "💎"},
            {"id": "bts", "name": "BTS", "emoji": "💜"},
            {"id": "stray-kids", "name": "Stray Kids", "emoji": "🐺"},
            {"id": "enhypen", "name": "ENHYPEN", "emoji": "🔥"},
            {"id": "txt", "name": "TXT", "emoji": "⭐"},
            {"id": "itzy", "name": "ITZY", "emoji": "✨"},
        ]

        # Convert groups to comparable format
        actual_groups_dict = {g["id"]: g for g in groups}

        for expected in expected_mobile_groups:
            actual = actual_groups_dict.get(expected["id"])
            assert (
                actual is not None
            ), f"Expected group {expected['id']} not found in API response"
            assert (
                actual["name"] == expected["name"]
            ), f"Name mismatch for {expected['id']}"
            assert (
                actual["emoji"] == expected["emoji"]
            ), f"Emoji mismatch for {expected['id']}"
