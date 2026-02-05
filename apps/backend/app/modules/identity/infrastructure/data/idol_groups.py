"""Static idol groups data source.

This module provides the complete list of K-pop idol groups available for user selection
during onboarding. The data is aligned with the mobile app's DEFAULT_IDOL_GROUPS constant.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class IdolGroup:
    """Idol group data class.

    Attributes:
        id: Unique identifier for the idol group (e.g., 'newjeans', 'ive')
        name: Display name of the idol group (e.g., 'NewJeans', 'IVE')
        emoji: Emoji representing the idol group (e.g., '👖', '🦢')
        sort_order: Display order in the UI (lower values appear first)
    """

    id: str
    name: str
    emoji: str
    sort_order: int


# Complete list of idol groups aligned with mobile app
# Source: apps/mobile/src/features/profile/constants/idolGroups.ts
IDOL_GROUPS: list[IdolGroup] = [
    IdolGroup(id="newjeans", name="NewJeans", emoji="👖", sort_order=1),
    IdolGroup(id="ive", name="IVE", emoji="🦢", sort_order=2),
    IdolGroup(id="aespa", name="aespa", emoji="🦋", sort_order=3),
    IdolGroup(id="le-sserafim", name="LE SSERAFIM", emoji="🌸", sort_order=4),
    IdolGroup(id="blackpink", name="BLACKPINK", emoji="💖", sort_order=5),
    IdolGroup(id="twice", name="TWICE", emoji="🍭", sort_order=6),
    IdolGroup(id="seventeen", name="SEVENTEEN", emoji="💎", sort_order=7),
    IdolGroup(id="bts", name="BTS", emoji="💜", sort_order=8),
    IdolGroup(id="stray-kids", name="Stray Kids", emoji="🐺", sort_order=9),
    IdolGroup(id="enhypen", name="ENHYPEN", emoji="🔥", sort_order=10),
    IdolGroup(id="txt", name="TXT", emoji="⭐", sort_order=11),
    IdolGroup(id="itzy", name="ITZY", emoji="✨", sort_order=12),
]


def get_all_idol_groups() -> list[IdolGroup]:
    """Get all available idol groups.

    Returns:
        List of all idol groups sorted by sort_order
    """
    return sorted(IDOL_GROUPS, key=lambda g: g.sort_order)


def get_idol_group_by_id(group_id: str) -> IdolGroup | None:
    """Get a specific idol group by ID.

    Args:
        group_id: The idol group ID to lookup

    Returns:
        The idol group if found, None otherwise
    """
    for group in IDOL_GROUPS:
        if group.id == group_id:
            return group
    return None
