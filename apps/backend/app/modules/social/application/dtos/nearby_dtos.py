"""
DTOs for nearby search feature.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class NearbyCardResult:
    """
    Result item for nearby card search.

    Attributes:
        card_id: UUID of the card
        owner_id: UUID of the card owner
        distance_km: Distance from search origin in kilometers
        idol: Idol name (optional)
        idol_group: Idol group name (optional)
        album: Album name (optional)
        version: Card version (optional)
        rarity: Card rarity (optional)
        image_url: Card image URL (optional)
        owner_nickname: Owner's nickname (optional)
    """

    card_id: UUID
    owner_id: UUID
    distance_km: float
    idol: Optional[str] = None
    idol_group: Optional[str] = None
    album: Optional[str] = None
    version: Optional[str] = None
    rarity: Optional[str] = None
    image_url: Optional[str] = None
    owner_nickname: Optional[str] = None


@dataclass
class SearchNearbyRequest:
    """
    Request for searching nearby cards.

    Attributes:
        user_id: UUID of the requesting user
        lat: Latitude of search origin
        lng: Longitude of search origin
        radius_km: Search radius in kilometers (optional, defaults to config value)
    """

    user_id: UUID
    lat: float
    lng: float
    radius_km: Optional[float] = None
