"""
Report Router for Social Module
Handles user reports for inappropriate behavior
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.presentation.dependencies.auth import get_current_user_id
from app.modules.social.application.use_cases.reports.report_user_use_case import (
    ReportUserUseCase,
)
from app.modules.social.infrastructure.repositories.report_repository_impl import (
    ReportRepositoryImpl,
)
from app.modules.social.presentation.schemas.report_schemas import (
    ReportListResponse,
    ReportListResponseWrapper,
    ReportRequest,
    ReportResponse,
    ReportResponseWrapper,
)
from app.shared.infrastructure.database.connection import get_db_session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "",
    response_model=ReportResponseWrapper,
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
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReportResponseWrapper:
    """
    Submit a report for another user.

    Business rules:
    - Cannot report yourself
    - Reason must be one of the valid report reasons (see ReportReason enum)
    - Optional detailed description
    - Reports are reviewed by moderators

    Valid report reasons:
    - fraud: Suspected fraud/scam
    - fake_card: Fake card image
    - harassment: Harassment or abusive behavior
    - inappropriate_content: Inappropriate messages/images
    - spam: Spam or repeated unwanted messages
    - other: Other reasons (please specify in detail)
    """
    try:
        # Initialize repository and use case
        report_repo = ReportRepositoryImpl(session)
        use_case = ReportUserUseCase(report_repo)

        # Execute use case
        report = await use_case.execute(
            reporter_id=str(current_user_id),
            reported_user_id=str(request.reported_user_id),
            reason=request.reason,
            detail=request.detail,
        )

        data = ReportResponse(
            id=UUID(report.id),
            reporter_id=UUID(report.reporter_id),
            reported_user_id=UUID(report.reported_user_id),
            reason=report.reason,
            detail=report.detail,
            status="pending",  # Reports start as pending
            created_at=report.created_at,
        )
        
        return ReportResponseWrapper(data=data, meta=None, error=None)

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
    response_model=ReportListResponseWrapper,
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
) -> ReportListResponseWrapper:
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

        data = ReportListResponse(reports=report_responses, total=len(report_responses))
        return ReportListResponseWrapper(data=data, meta=None, error=None)

    except Exception as e:
        logger.error(f"Error getting reports: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reports",
        )
