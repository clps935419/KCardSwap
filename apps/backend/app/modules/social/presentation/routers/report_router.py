"""
Report Router for Social Module
Handles user reports for inappropriate behavior
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id
from app.modules.social.application.use_cases.reports.report_user_use_case import (
    ReportUserUseCase,
)
from app.modules.social.infrastructure.repositories.report_repository_impl import (
    ReportRepositoryImpl,
)
from app.modules.social.presentation.dependencies.use_cases import (
    get_report_user_use_case,
)
from app.modules.social.presentation.schemas.report_schemas import (
    ReportListResponse,
    ReportRequest,
    ReportResponse,
)
from app.shared.infrastructure.database.connection import get_db_session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Report submitted successfully"},
        400: {"description": "Bad request (validation failed)"},
        401: {"description": "Unauthorized (not logged in)"},
        422: {"description": "Unprocessable entity (cannot report user)"},
        500: {"description": "Internal server error"},
    },
    summary="Submit report",
    description="Submit a report for inappropriate behavior or content",
)
async def submit_report(
    request: ReportRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ReportUserUseCase, Depends(get_report_user_use_case)],
) -> ReportResponse:
    """
    Submit a report for another user.

    Business rules:
    - Cannot report yourself
    - Reason is required (e.g., "Spam", "Harassment", "Scam")
    - Optional detailed description
    - Reports are reviewed by moderators

    Common report reasons:
    - Inappropriate behavior
    - Spam
    - Scam
    - Harassment
    - Fake cards
    - Other (please specify in detail)
    """
    try:
        # Execute use case
        report = await use_case.execute(
            reporter_id=str(current_user_id),
            reported_user_id=str(request.reported_user_id),
            reason=request.reason,
            detail=request.detail,
        )

        return ReportResponse(
            id=UUID(report.id),
            reporter_id=UUID(report.reporter_id),
            reported_user_id=UUID(report.reported_user_id),
            reason=report.reason,
            detail=report.detail,
            status="pending",  # Reports start as pending
            created_at=report.created_at,
        )

    except ValueError as e:
        logger.warning(f"Report validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit report",
        )


@router.get(
    "",
    response_model=ReportListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Reports retrieved successfully"},
        401: {"description": "Unauthorized (not logged in)"},
        500: {"description": "Internal server error"},
    },
    summary="Get my reports",
    description="Get reports submitted by the current user",
)
async def get_my_reports(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReportListResponse:
    """
    Get reports submitted by the current user.

    Returns list of reports with:
    - Reported user information
    - Reason and details
    - Status (pending, reviewed, resolved)
    - Timestamp

    Allows users to track their submitted reports.
    """
    try:
        # Initialize repository
        report_repo = ReportRepositoryImpl(session)

        # Get reports by reporter
        reports = await report_repo.find_by_reporter(str(current_user_id))

        # Convert to response format
        report_responses = [
            ReportResponse(
                id=UUID(report.id),
                reporter_id=UUID(report.reporter_id),
                reported_user_id=UUID(report.reported_user_id),
                reason=report.reason,
                detail=report.detail,
                status="pending",  # TODO: Add status field to Report entity
                created_at=report.created_at,
            )
            for report in reports
        ]

        return ReportListResponse(reports=report_responses, total=len(report_responses))

    except Exception as e:
        logger.error(f"Error getting reports: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reports",
        )
