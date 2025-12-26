"""
Purchase Token Repository Interface - For tracking Google Play purchase tokens
"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class IPurchaseTokenRepository(ABC):
    """Repository interface for tracking purchase tokens to prevent replay attacks"""

    @abstractmethod
    async def is_token_used(self, purchase_token: str) -> bool:
        """Check if purchase token has been used"""
        pass

    @abstractmethod
    async def get_user_id_for_token(self, purchase_token: str) -> Optional[UUID]:
        """Get the user ID that this token is bound to"""
        pass

    @abstractmethod
    async def bind_token_to_user(
        self,
        purchase_token: str,
        user_id: UUID,
        product_id: str,
        platform: str = "android"
    ) -> None:
        """
        Bind a purchase token to a user.
        Raises exception if token is already bound to a different user.
        """
        pass

    @abstractmethod
    async def verify_token_ownership(self, purchase_token: str, user_id: UUID) -> bool:
        """Verify that the token belongs to the given user"""
        pass
