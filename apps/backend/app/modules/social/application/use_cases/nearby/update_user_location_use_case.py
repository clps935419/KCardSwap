"""
Use case for updating user's location.
"""

from uuid import UUID

from app.modules.identity.domain.repositories.i_profile_repository import (
    IProfileRepository,
)


class UpdateUserLocationUseCase:
    """
    Use case for updating user's last known location.

    This records the user's location in their profile for nearby search functionality.
    """

    def __init__(self, profile_repository: IProfileRepository):
        """
        Initialize the use case.

        Args:
            profile_repository: Profile repository for data access
        """
        self.profile_repository = profile_repository

    async def execute(self, user_id: UUID, lat: float, lng: float) -> None:
        """
        Update user's location.

        Args:
            user_id: User's UUID
            lat: Latitude (-90 to 90)
            lng: Longitude (-180 to 180)

        Raises:
            ValueError: If coordinates are invalid
            Exception: If profile not found
        """
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= lng <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        # Get user's profile
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            raise Exception(f"Profile not found for user {user_id}")

        # Update location
        profile.update_location(lat, lng)

        # Save profile
        await self.profile_repository.save(profile)
