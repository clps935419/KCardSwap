"""
Use case for updating user's location.
"""

from uuid import UUID

from app.shared.domain.contracts.i_profile_query_service import IProfileQueryService


class UpdateUserLocationUseCase:
    """
    Use case for updating user's last known location.

    This records the user's location in their profile for nearby search functionality.
    """

    def __init__(self, profile_service: IProfileQueryService):
        """
        Initialize the use case.

        Args:
            profile_service: Profile query service for data access
        """
        self.profile_service = profile_service

    async def execute(self, user_id: UUID, lat: float, lng: float) -> None:
        """
        Update user's location.

        Args:
            user_id: User's UUID
            lat: Latitude (-90 to 90)
            lng: Longitude (-180 to 180)

        Raises:
            ValueError: If coordinates are invalid
            Exception: If profile not found or update fails
        """
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= lng <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        # Update location using the service
        success = await self.profile_service.update_user_location(user_id, lat, lng)
        if not success:
            raise Exception(f"Failed to update location for user {user_id}")
