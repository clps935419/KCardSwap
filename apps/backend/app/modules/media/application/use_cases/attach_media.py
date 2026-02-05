"""Attach media use cases - Attach confirmed media to posts or gallery cards."""
from dataclasses import dataclass
from uuid import UUID

from app.modules.media.domain.repositories.i_media_repository import IMediaRepository


@dataclass
class AttachMediaRequest:
    """Request for attaching media."""
    user_id: UUID
    media_id: UUID
    target_type: str  # "post" or "gallery_card"
    target_id: UUID


@dataclass
class AttachMediaResponse:
    """Response after attaching media."""
    media_id: UUID
    status: str
    attached_to: str
    target_id: UUID


class AttachMediaUseCase:
    """Use case for attaching confirmed media to posts or gallery cards.

    This is step 3 of the media upload flow: presign → upload → confirm → attach.

    FR-007: System must only allow attaching confirmed media owned by the user.
    """

    def __init__(
        self,
        media_repository: IMediaRepository,
    ):
        self.media_repository = media_repository

    async def execute(self, request: AttachMediaRequest) -> AttachMediaResponse:
        """Attach confirmed media to target entity.

        Args:
            request: Attach request

        Returns:
            Attached media details

        Raises:
            ValueError: If media not found, not owned, or not confirmed
        """
        # Get media asset
        media = await self.media_repository.get_by_id(request.media_id)
        if not media:
            raise ValueError(f"Media {request.media_id} not found")

        # FR-007: Verify ownership
        if not media.is_owned_by(request.user_id):
            raise ValueError(f"Media {request.media_id} is not owned by user {request.user_id}")

        # FR-007: Verify media is confirmed
        if not media.is_confirmed():
            raise ValueError(
                f"Media {request.media_id} must be confirmed before attaching. "
                f"Current status: {media.status.value}"
            )

        # Mark as attached
        media.attach(target_type=request.target_type, target_id=request.target_id)

        # Update in database
        await self.media_repository.update(media)

        return AttachMediaResponse(
            media_id=media.id,
            status=media.status.value,
            attached_to=request.target_type,
            target_id=request.target_id,
        )
