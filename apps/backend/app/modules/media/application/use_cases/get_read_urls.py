"""Get Read URLs Use Case for Phase 9.

Batch generate signed read URLs for media assets.
Login-only access - users can get read URLs for any confirmed or attached media.
"""
from dataclasses import dataclass
from typing import Dict, List
from uuid import UUID

from app.modules.media.domain.entities.media_asset import MediaStatus
from app.modules.media.domain.repositories.i_media_repository import IMediaRepository
from app.shared.infrastructure.external.gcs_storage_service import GCSStorageService


@dataclass
class GetReadUrlsRequest:
    """Request to get read URLs for media assets."""

    user_id: UUID  # Must be logged in
    media_asset_ids: List[UUID]


@dataclass
class GetReadUrlsResult:
    """Result containing signed read URLs."""

    urls: Dict[str, str]  # media_id -> signed_url
    expires_in_minutes: int


class GetReadUrlsUseCase:
    """Use case for batch generating signed read URLs.

    Phase 9 requirement: Login-only access to images.
    Users can get read URLs for any confirmed or attached media assets.
    """

    def __init__(
        self,
        media_repository: IMediaRepository,
        storage_service: GCSStorageService,
        read_url_ttl_minutes: int = 10,  # Default 10 minutes TTL
    ):
        self.media_repository = media_repository
        self.storage_service = storage_service
        self.read_url_ttl_minutes = read_url_ttl_minutes

    async def execute(self, request: GetReadUrlsRequest) -> GetReadUrlsResult:
        """Generate signed read URLs for requested media assets.

        Args:
            request: GetReadUrlsRequest containing media_asset_ids

        Returns:
            GetReadUrlsResult with media_id -> url mapping

        Raises:
            ValueError: If user is not authenticated (user_id is None)
        """
        if not request.user_id:
            raise ValueError("User must be logged in to get read URLs")

        # Get media assets from repository
        media_assets = await self.media_repository.get_by_ids(request.media_asset_ids)

        # Filter only confirmed or attached media
        # (pending media should not be accessible)
        accessible_media = [
            media
            for media in media_assets
            if media.status in [MediaStatus.CONFIRMED, MediaStatus.ATTACHED]
        ]

        # Generate signed URLs for each accessible media
        urls = {}
        for media in accessible_media:
            signed_url = self.storage_service.generate_download_signed_url(
                blob_name=media.gcs_blob_name,
                expiration_minutes=self.read_url_ttl_minutes,
            )
            urls[str(media.id)] = signed_url

        return GetReadUrlsResult(
            urls=urls,
            expires_in_minutes=self.read_url_ttl_minutes,
        )
