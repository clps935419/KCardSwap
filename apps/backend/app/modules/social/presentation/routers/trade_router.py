"""
Trade Router for Social Module
Handles trade proposals, acceptance, rejection, cancellation, completion, and history
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id
from app.modules.social.application.use_cases.trades.accept_trade_use_case import (
    AcceptTradeUseCase,
)
from app.modules.social.application.use_cases.trades.cancel_trade_use_case import (
    CancelTradeUseCase,
)
from app.modules.social.application.use_cases.trades.complete_trade_use_case import (
    CompleteTradeUseCase,
)
from app.modules.social.application.use_cases.trades.create_trade_proposal_use_case import (
    CreateTradeProposalRequest,
    CreateTradeProposalUseCase,
)
from app.modules.social.application.use_cases.trades.get_trade_history_use_case import (
    GetTradeHistoryUseCase,
)
from app.modules.social.application.use_cases.trades.reject_trade_use_case import (
    RejectTradeUseCase,
)
from app.modules.social.domain.repositories.trade_repository import ITradeRepository
from app.modules.social.presentation.dependencies.use_cases import (
    get_accept_trade_use_case,
    get_cancel_trade_use_case,
    get_complete_trade_use_case,
    get_create_trade_proposal_use_case,
    get_reject_trade_use_case,
    get_trade_history_use_case,
    get_trade_repository,
)
from app.modules.social.presentation.schemas.trade_schemas import (
    CreateTradeRequest,
    TradeHistoryResponse,
    TradeItemResponse,
    TradeResponse,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/trades", tags=["Trades"])


@router.post(
    "",
    response_model=TradeResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Trade proposal created successfully"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        422: {"description": "Unprocessable entity (validation error)"},
        500: {"description": "Internal server error"},
    },
    summary="Create trade proposal",
    description="Create a new trade proposal between two users",
)
async def create_trade(
    request: CreateTradeRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[CreateTradeProposalUseCase, Depends(get_create_trade_proposal_use_case)],
    trade_repo: Annotated[ITradeRepository, Depends(get_trade_repository)],
) -> TradeResponse:
    """
    Create a new trade proposal.

    Business rules:
    - Must be friends with responder
    - All cards must exist and be available
    - Maximum 3 active trades between two users
    """
    try:
        # Execute use case
        trade = await use_case.execute(
            CreateTradeProposalRequest(
                initiator_id=current_user_id,
                responder_id=request.responder_id,
                initiator_card_ids=request.initiator_card_ids,
                responder_card_ids=request.responder_card_ids,
            )
        )

        # Get items for response
        items = await trade_repo.get_items_by_trade_id(trade.id)

        return TradeResponse(
            id=trade.id,
            initiator_id=trade.initiator_id,
            responder_id=trade.responder_id,
            status=trade.status,
            accepted_at=trade.accepted_at,
            initiator_confirmed_at=trade.initiator_confirmed_at,
            responder_confirmed_at=trade.responder_confirmed_at,
            completed_at=trade.completed_at,
            canceled_at=trade.canceled_at,
            created_at=trade.created_at,
            updated_at=trade.updated_at,
            items=[
                TradeItemResponse(
                    id=item.id,
                    trade_id=item.trade_id,
                    card_id=item.card_id,
                    owner_side=item.owner_side,
                    created_at=item.created_at,
                )
                for item in items
            ],
        )

    except ValueError as e:
        logger.warning(f"Trade creation validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating trade: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create trade",
        )


@router.post(
    "/{trade_id}/accept",
    response_model=TradeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Trade accepted successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        404: {"description": "Trade not found"},
        422: {"description": "Unprocessable entity (cannot accept trade)"},
        500: {"description": "Internal server error"},
    },
    summary="Accept trade proposal",
    description="Accept a trade proposal (responder only)",
)
async def accept_trade(
    trade_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[AcceptTradeUseCase, Depends(get_accept_trade_use_case)],
    trade_repo: Annotated[ITradeRepository, Depends(get_trade_repository)],
) -> TradeResponse:
    """Accept a trade proposal."""
    try:
        trade = await use_case.execute(trade_id, current_user_id)
        items = await trade_repo.get_items_by_trade_id(trade.id)

        return TradeResponse(
            id=trade.id,
            initiator_id=trade.initiator_id,
            responder_id=trade.responder_id,
            status=trade.status,
            accepted_at=trade.accepted_at,
            initiator_confirmed_at=trade.initiator_confirmed_at,
            responder_confirmed_at=trade.responder_confirmed_at,
            completed_at=trade.completed_at,
            canceled_at=trade.canceled_at,
            created_at=trade.created_at,
            updated_at=trade.updated_at,
            items=[
                TradeItemResponse(
                    id=item.id,
                    trade_id=item.trade_id,
                    card_id=item.card_id,
                    owner_side=item.owner_side,
                    created_at=item.created_at,
                )
                for item in items
            ],
        )

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        logger.warning(f"Trade acceptance validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error accepting trade: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept trade",
        )


@router.post(
    "/{trade_id}/reject",
    response_model=TradeResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject trade proposal",
    description="Reject a trade proposal (responder only)",
)
async def reject_trade(
    trade_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[RejectTradeUseCase, Depends(get_reject_trade_use_case)],
    trade_repo: Annotated[ITradeRepository, Depends(get_trade_repository)],
) -> TradeResponse:
    """Reject a trade proposal."""
    try:
        trade = await use_case.execute(trade_id, current_user_id)
        items = await trade_repo.get_items_by_trade_id(trade.id)

        return TradeResponse(
            id=trade.id,
            initiator_id=trade.initiator_id,
            responder_id=trade.responder_id,
            status=trade.status,
            accepted_at=trade.accepted_at,
            initiator_confirmed_at=trade.initiator_confirmed_at,
            responder_confirmed_at=trade.responder_confirmed_at,
            completed_at=trade.completed_at,
            canceled_at=trade.canceled_at,
            created_at=trade.created_at,
            updated_at=trade.updated_at,
            items=[
                TradeItemResponse(
                    id=item.id,
                    trade_id=item.trade_id,
                    card_id=item.card_id,
                    owner_side=item.owner_side,
                    created_at=item.created_at,
                )
                for item in items
            ],
        )

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        logger.warning(f"Trade rejection validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error rejecting trade: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject trade",
        )


@router.post(
    "/{trade_id}/cancel",
    response_model=TradeResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel trade",
    description="Cancel a trade (either party can cancel)",
)
async def cancel_trade(
    trade_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[CancelTradeUseCase, Depends(get_cancel_trade_use_case)],
    trade_repo: Annotated[ITradeRepository, Depends(get_trade_repository)],
) -> TradeResponse:
    """Cancel a trade."""
    try:
        trade = await use_case.execute(trade_id, current_user_id)
        items = await trade_repo.get_items_by_trade_id(trade.id)

        return TradeResponse(
            id=trade.id,
            initiator_id=trade.initiator_id,
            responder_id=trade.responder_id,
            status=trade.status,
            accepted_at=trade.accepted_at,
            initiator_confirmed_at=trade.initiator_confirmed_at,
            responder_confirmed_at=trade.responder_confirmed_at,
            completed_at=trade.completed_at,
            canceled_at=trade.canceled_at,
            created_at=trade.created_at,
            updated_at=trade.updated_at,
            items=[
                TradeItemResponse(
                    id=item.id,
                    trade_id=item.trade_id,
                    card_id=item.card_id,
                    owner_side=item.owner_side,
                    created_at=item.created_at,
                )
                for item in items
            ],
        )

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        logger.warning(f"Trade cancellation validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error canceling trade: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel trade",
        )


@router.post(
    "/{trade_id}/complete",
    response_model=TradeResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm trade completion",
    description="Confirm trade completion (each party confirms independently)",
)
async def complete_trade(
    trade_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[CompleteTradeUseCase, Depends(get_complete_trade_use_case)],
    trade_repo: Annotated[ITradeRepository, Depends(get_trade_repository)],
) -> TradeResponse:
    """
    Confirm trade completion.

    Each party confirms independently. When both confirm, status becomes 'completed'.
    Enforces 48h timeout from acceptance.
    """
    try:
        trade = await use_case.execute(trade_id, current_user_id)
        items = await trade_repo.get_items_by_trade_id(trade.id)

        return TradeResponse(
            id=trade.id,
            initiator_id=trade.initiator_id,
            responder_id=trade.responder_id,
            status=trade.status,
            accepted_at=trade.accepted_at,
            initiator_confirmed_at=trade.initiator_confirmed_at,
            responder_confirmed_at=trade.responder_confirmed_at,
            completed_at=trade.completed_at,
            canceled_at=trade.canceled_at,
            created_at=trade.created_at,
            updated_at=trade.updated_at,
            items=[
                TradeItemResponse(
                    id=item.id,
                    trade_id=item.trade_id,
                    card_id=item.card_id,
                    owner_side=item.owner_side,
                    created_at=item.created_at,
                )
                for item in items
            ],
        )

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        logger.warning(f"Trade completion validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing trade: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete trade",
        )


@router.get(
    "/history",
    response_model=TradeHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get trade history",
    description="Get all trades for current user (as initiator or responder)",
)
async def get_trade_history(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetTradeHistoryUseCase, Depends(get_trade_history_use_case)],
    trade_repo: Annotated[ITradeRepository, Depends(get_trade_repository)],
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> TradeHistoryResponse:
    """Get trade history for current user."""
    try:
        trades = await use_case.execute(
            user_id=current_user_id,
            limit=limit,
            offset=offset,
        )

        # Get items for each trade
        trade_responses = []
        for trade in trades:
            items = await trade_repo.get_items_by_trade_id(trade.id)
            trade_responses.append(
                TradeResponse(
                    id=trade.id,
                    initiator_id=trade.initiator_id,
                    responder_id=trade.responder_id,
                    status=trade.status,
                    accepted_at=trade.accepted_at,
                    initiator_confirmed_at=trade.initiator_confirmed_at,
                    responder_confirmed_at=trade.responder_confirmed_at,
                    completed_at=trade.completed_at,
                    canceled_at=trade.canceled_at,
                    created_at=trade.created_at,
                    updated_at=trade.updated_at,
                    items=[
                        TradeItemResponse(
                            id=item.id,
                            trade_id=item.trade_id,
                            card_id=item.card_id,
                            owner_side=item.owner_side,
                            created_at=item.created_at,
                        )
                        for item in items
                    ],
                )
            )

        return TradeHistoryResponse(
            trades=trade_responses,
            total=len(trades),
            limit=limit,
            offset=offset,
        )

    except ValueError as e:
        logger.warning(f"Trade history validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting trade history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trade history",
        )
