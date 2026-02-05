"""
Unit tests for Geolocation utilities

Tests the haversine distance calculation.
"""



from app.modules.social.infrastructure.utils.geolocation import haversine_distance


class TestGeolocation:
    """Test geolocation utilities"""

    def test_haversine_distance_taipei_to_taichung(self):
        """Test distance between Taipei and Taichung"""
        # Arrange
        taipei_lat, taipei_lng = 25.0330, 121.5654
        taichung_lat, taichung_lng = 24.1477, 120.6736

        # Act
        distance = haversine_distance(taipei_lat, taipei_lng, taichung_lat, taichung_lng)

        # Assert
        # Expected distance is approximately 130-135 km
        assert 130 < distance < 140

    def test_haversine_distance_same_location(self):
        """Test distance between same coordinates is zero"""
        # Arrange
        lat, lng = 25.0330, 121.5654

        # Act
        distance = haversine_distance(lat, lng, lat, lng)

        # Assert
        assert distance == 0.0

    def test_haversine_distance_taipei_to_kaohsiung(self):
        """Test distance between Taipei and Kaohsiung"""
        # Arrange
        taipei_lat, taipei_lng = 25.0330, 121.5654
        kaohsiung_lat, kaohsiung_lng = 22.6273, 120.3014

        # Act
        distance = haversine_distance(
            taipei_lat, taipei_lng, kaohsiung_lat, kaohsiung_lng
        )

        # Assert
        # Expected distance is approximately 290-300 km
        assert 290 < distance < 305

    def test_haversine_distance_short_distance(self):
        """Test short distance calculation"""
        # Arrange - Two points very close together (~1km)
        lat1, lng1 = 25.0330, 121.5654
        lat2, lng2 = 25.0420, 121.5654

        # Act
        distance = haversine_distance(lat1, lng1, lat2, lng2)

        # Assert
        assert 0.5 < distance < 1.5

    def test_haversine_distance_north_to_south(self):
        """Test distance calculation for north-south movement"""
        # Arrange - Pure latitude difference
        lat1, lng1 = 25.0, 121.0
        lat2, lng2 = 26.0, 121.0

        # Act
        distance = haversine_distance(lat1, lng1, lat2, lng2)

        # Assert
        # 1 degree latitude is approximately 111 km
        assert 110 < distance < 112

    def test_haversine_distance_east_to_west(self):
        """Test distance calculation for east-west movement"""
        # Arrange - Pure longitude difference
        lat1, lng1 = 25.0, 121.0
        lat2, lng2 = 25.0, 122.0

        # Act
        distance = haversine_distance(lat1, lng1, lat2, lng2)

        # Assert
        # 1 degree longitude varies by latitude, at 25°N it's about 101 km
        assert 99 < distance < 103

    def test_haversine_distance_negative_coordinates(self):
        """Test distance with negative coordinates (southern hemisphere)"""
        # Arrange - Sydney and Melbourne (southern hemisphere)
        sydney_lat, sydney_lng = -33.8688, 151.2093
        melbourne_lat, melbourne_lng = -37.8136, 144.9631

        # Act
        distance = haversine_distance(
            sydney_lat, sydney_lng, melbourne_lat, melbourne_lng
        )

        # Assert
        # Expected distance is approximately 700-750 km
        assert 700 < distance < 800

    def test_haversine_distance_crossing_equator(self):
        """Test distance crossing the equator"""
        # Arrange
        lat1, lng1 = 1.0, 100.0  # North of equator
        lat2, lng2 = -1.0, 100.0  # South of equator

        # Act
        distance = haversine_distance(lat1, lng1, lat2, lng2)

        # Assert
        # 2 degrees latitude is approximately 222 km
        assert 220 < distance < 224

    def test_haversine_distance_symmetry(self):
        """Test that distance is symmetric (A to B = B to A)"""
        # Arrange
        lat1, lng1 = 25.0330, 121.5654
        lat2, lng2 = 24.1477, 120.6736

        # Act
        distance_forward = haversine_distance(lat1, lng1, lat2, lng2)
        distance_backward = haversine_distance(lat2, lng2, lat1, lng1)

        # Assert
        assert distance_forward == distance_backward

    def test_haversine_distance_precise_calculation(self):
        """Test precise calculation for known distance"""
        # Arrange - Coordinates with known precise distance
        lat1, lng1 = 0.0, 0.0
        lat2, lng2 = 0.0, 1.0

        # Act
        distance = haversine_distance(lat1, lng1, lat2, lng2)

        # Assert
        # At equator, 1 degree longitude is approximately 111.32 km
        assert 111 < distance < 112

    def test_haversine_distance_large_distance(self):
        """Test large distance calculation (across continents)"""
        # Arrange - Tokyo to New York
        tokyo_lat, tokyo_lng = 35.6762, 139.6503
        ny_lat, ny_lng = 40.7128, -74.0060

        # Act
        distance = haversine_distance(tokyo_lat, tokyo_lng, ny_lat, ny_lng)

        # Assert
        # Expected distance is approximately 10,800-11,000 km
        assert 10700 < distance < 11100
