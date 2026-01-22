"""Unit tests for idol groups static data."""

from app.modules.identity.infrastructure.data.idol_groups import (
    IDOL_GROUPS,
    get_all_idol_groups,
    get_idol_group_by_id,
)


class TestIdolGroupsData:
    """Test idol groups static data source."""

    def test_idol_groups_count(self):
        """Test that we have exactly 12 idol groups."""
        assert len(IDOL_GROUPS) == 12

    def test_all_idol_groups_have_required_fields(self):
        """Test that all idol groups have id, name, emoji, and sort_order."""
        for group in IDOL_GROUPS:
            assert group.id is not None
            assert group.name is not None
            assert group.emoji is not None
            assert group.sort_order is not None
            assert isinstance(group.id, str)
            assert isinstance(group.name, str)
            assert isinstance(group.emoji, str)
            assert isinstance(group.sort_order, int)

    def test_idol_group_ids_are_unique(self):
        """Test that all idol group IDs are unique."""
        ids = [group.id for group in IDOL_GROUPS]
        assert len(ids) == len(set(ids)), "Idol group IDs must be unique"

    def test_sort_orders_are_unique(self):
        """Test that all sort orders are unique."""
        sort_orders = [group.sort_order for group in IDOL_GROUPS]
        assert len(sort_orders) == len(
            set(sort_orders)
        ), "Sort orders must be unique"

    def test_get_all_idol_groups_returns_sorted_list(self):
        """Test that get_all_idol_groups returns groups sorted by sort_order."""
        groups = get_all_idol_groups()

        # Check we got all groups
        assert len(groups) == 12

        # Check they are sorted by sort_order
        for i in range(len(groups) - 1):
            assert (
                groups[i].sort_order < groups[i + 1].sort_order
            ), "Groups should be sorted by sort_order"

    def test_get_all_idol_groups_first_is_newjeans(self):
        """Test that NewJeans is the first group (sort_order=1)."""
        groups = get_all_idol_groups()
        first_group = groups[0]

        assert first_group.id == "newjeans"
        assert first_group.name == "NewJeans"
        assert first_group.emoji == "👖"
        assert first_group.sort_order == 1

    def test_get_idol_group_by_id_success(self):
        """Test getting a specific idol group by ID."""
        group = get_idol_group_by_id("aespa")

        assert group is not None
        assert group.id == "aespa"
        assert group.name == "aespa"
        assert group.emoji == "🦋"

    def test_get_idol_group_by_id_not_found(self):
        """Test getting a non-existent idol group returns None."""
        group = get_idol_group_by_id("non-existent-group")
        assert group is None

    def test_idol_groups_match_mobile_constants(self):
        """Test that idol groups match mobile app constants."""
        # Expected groups from mobile: apps/mobile/src/features/profile/constants/idolGroups.ts
        expected_groups = [
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

        # Create a dict for easy lookup
        groups_dict = {group.id: group for group in IDOL_GROUPS}

        # Verify each expected group exists with correct data
        for expected in expected_groups:
            group = groups_dict.get(expected["id"])
            assert (
                group is not None
            ), f"Expected group {expected['id']} not found"
            assert (
                group.name == expected["name"]
            ), f"Name mismatch for {expected['id']}"
            assert (
                group.emoji == expected["emoji"]
            ), f"Emoji mismatch for {expected['id']}"

    def test_key_idol_groups_present(self):
        """Test that key idol groups are present."""
        key_groups = ["newjeans", "ive", "aespa", "blackpink", "bts"]

        for group_id in key_groups:
            group = get_idol_group_by_id(group_id)
            assert (
                group is not None
            ), f"Key idol group {group_id} should be present"
