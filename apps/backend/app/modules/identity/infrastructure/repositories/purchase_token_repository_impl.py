"""
Purchase Token Repository Implementation
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.modules.identity.domain.repositories.i_purchase_token_repository import (
    IPurchaseTokenRepository,
)
from app.modules.identity.infrastructure.database.models.purchase_token_model import (
    PurchaseTokenModel,
)
from app.shared.presentation.exceptions.api_exceptions import ConflictException


class IPurchaseTokenRepositoryImpl(IPurchaseTokenRepository):
    """SQLAlchemy implementation of IPurchaseTokenRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_token_used(self, purchase_token: str) -> bool:
        """Check if purchase token has been used"""
        result = await self.session.execute(
            select(PurchaseTokenModel).where(
                PurchaseTokenModel.purchase_token == purchase_token
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_user_id_for_token(self, purchase_token: str) -> Optional[UUID]:
        """Get the user ID that this token is bound to"""
        result = await self.session.execute(
            select(PurchaseTokenModel.user_id).where(
                PurchaseTokenModel.purchase_token == purchase_token
            )
        )
        user_id = result.scalar_one_or_none()
        return user_id

    async def bind_token_to_user(
        self,
        purchase_token: str,
        user_id: UUID,
        product_id: str,
        platform: str = "android",
    ) -> None:
        """
        Bind a purchase token to a user.
        Raises ConflictException if token is already bound to a different user.
        """
        # Check if token is already bound
        existing_user_id = await self.get_user_id_for_token(purchase_token)

        if existing_user_id is not None:
            if existing_user_id != user_id:
                # Token is bound to a different user - replay attack
                raise ConflictException(
                    "PURCHASE_TOKEN_ALREADY_USED", "此購買已被其他帳號使用"
                )
            # Token already bound to same user - idempotent, do nothing
            return

        # Bind token to user
        model = PurchaseTokenModel(
            purchase_token=purchase_token,
            user_id=user_id,
            product_id=product_id,
            platform=platform,
        )

        try:
            self.session.add(model)
            await self.session.flush()
        except IntegrityError:
            # Race condition: token was bound between check and insert
            # Re-check ownership
            existing_user_id = await self.get_user_id_for_token(purchase_token)
            if existing_user_id != user_id:
                raise ConflictException(
                    "PURCHASE_TOKEN_ALREADY_USED", "此購買已被其他帳號使用"
                )
            # Same user - idempotent

    async def verify_token_ownership(self, purchase_token: str, user_id: UUID) -> bool:
        """Verify that the token belongs to the given user"""
        existing_user_id = await self.get_user_id_for_token(purchase_token)
        return existing_user_id == user_id
