"""
Geolocation utilities for calculating distances between coordinates.
"""

import math


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.

    Args:
        lat1: Latitude of first point in degrees
        lng1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lng2: Longitude of second point in degrees

    Returns:
        Distance in kilometers

    Example:
        >>> haversine_distance(25.0330, 121.5654, 24.1477, 120.6736)  # Taipei to Taichung
        120.5
    """
    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    distance = EARTH_RADIUS_KM * c

    return distance
