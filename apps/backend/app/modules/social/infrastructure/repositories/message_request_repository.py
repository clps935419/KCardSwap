"""MessageRequest Repository Implementation"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.message_request import (
    MessageRequest,
    RequestStatus,
)
from app.modules.social.domain.repositories.i_message_request_repository import (
    IMessageRequestRepository,
)
from app.modules.social.infrastructure.database.models.message_request_model import (
    MessageRequestModel,
)


class MessageRequestRepository(IMessageRequestRepository):
    """Repository implementation for MessageRequest using SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: MessageRequestModel) -> MessageRequest:
        """Convert ORM model to domain entity"""
        return MessageRequest(
            id=str(model.id),
            sender_id=str(model.sender_id),
            recipient_id=str(model.recipient_id),
            initial_message=model.initial_message,
            post_id=str(model.post_id) if model.post_id else None,
            status=RequestStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            thread_id=str(model.thread_id) if model.thread_id else None,
        )

    def _to_model(self, entity: MessageRequest) -> MessageRequestModel:
        """Convert domain entity to ORM model"""
        return MessageRequestModel(
            id=UUID(entity.id),
            sender_id=UUID(entity.sender_id),
            recipient_id=UUID(entity.recipient_id),
            initial_message=entity.initial_message,
            post_id=UUID(entity.post_id) if entity.post_id else None,
            status=entity.status.value,
            thread_id=UUID(entity.thread_id) if entity.thread_id else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, message_request: MessageRequest) -> MessageRequest:
        """Create a new message request"""
        model = self._to_model(message_request)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, request_id: str) -> Optional[MessageRequest]:
        """Get message request by ID"""
        stmt = select(MessageRequestModel).where(
            MessageRequestModel.id == UUID(request_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_pending_between_users(
        self, user_a_id: str, user_b_id: str
    ) -> Optional[MessageRequest]:
        """Find pending message request between two users (either direction)"""
        stmt = select(MessageRequestModel).where(
            and_(
                or_(
                    and_(
                        MessageRequestModel.sender_id == UUID(user_a_id),
                        MessageRequestModel.recipient_id == UUID(user_b_id),
                    ),
                    and_(
                        MessageRequestModel.sender_id == UUID(user_b_id),
                        MessageRequestModel.recipient_id == UUID(user_a_id),
                    ),
                ),
                MessageRequestModel.status == "pending",
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_requests_for_recipient(
        self, recipient_id: str, status: Optional[RequestStatus] = None
    ) -> List[MessageRequest]:
        """Get all message requests for a recipient"""
        stmt = select(MessageRequestModel).where(
            MessageRequestModel.recipient_id == UUID(recipient_id)
        )

        if status:
            stmt = stmt.where(MessageRequestModel.status == status.value)

        stmt = stmt.order_by(MessageRequestModel.created_at.desc())

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, message_request: MessageRequest) -> MessageRequest:
        """Update an existing message request"""
        stmt = select(MessageRequestModel).where(
            MessageRequestModel.id == UUID(message_request.id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one()

        model.status = message_request.status.value
        model.thread_id = (
            UUID(message_request.thread_id) if message_request.thread_id else None
        )
        model.updated_at = message_request.updated_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, request_id: str) -> None:
        """Delete a message request"""
        stmt = select(MessageRequestModel).where(
            MessageRequestModel.id == UUID(request_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        await self.session.delete(model)
        await self.session.flush()
