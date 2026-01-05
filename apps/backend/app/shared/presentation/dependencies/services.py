"""
Shared Service Dependencies

FastAPI dependencies for getting services from the global injector.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.contracts.i_profile_query_service import IProfileQueryService
from app.shared.domain.contracts.i_subscription_query_service import (
    ISubscriptionQueryService,
)
from app.shared.infrastructure.database.connection import get_db_session


async def get_subscription_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ISubscriptionQueryService:
    """
    Get subscription query service.
    
    Creates the implementation from IdentityModule using the provided session.
    """
    # Import implementation here to avoid circular imports
    from app.modules.identity.application.services.subscription_query_service_impl import (
        SubscriptionQueryServiceImpl,
    )
    from app.modules.identity.infrastructure.repositories.subscription_repository_impl import (
        SubscriptionRepositoryImpl,
    )
    
    subscription_repo = SubscriptionRepositoryImpl(session)
    return SubscriptionQueryServiceImpl(subscription_repository=subscription_repo)


async def get_profile_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IProfileQueryService:
    """
    Get profile query service.
    
    Creates the implementation from IdentityModule using the provided session.
    """
    # Import implementation here to avoid circular imports
    from app.modules.identity.application.services.profile_query_service_impl import (
        ProfileQueryServiceImpl,
    )
    from app.modules.identity.infrastructure.repositories.profile_repository_impl import (
        ProfileRepositoryImpl,
    )
    
    profile_repo = ProfileRepositoryImpl(session)
    return ProfileQueryServiceImpl(profile_repository=profile_repo)
