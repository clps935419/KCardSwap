"""Report User Use Case"""
import uuid
from datetime import datetime
from typing import Optional

from app.modules.social.domain.entities.report import Report, ReportReason
from app.modules.social.domain.repositories.report_repository import ReportRepository


class ReportUserUseCase:
    """
    Use case for reporting a user for violations
    
    Business Rules:
    - User cannot report themselves
    - Report reason must be valid
    - Optional detailed explanation can be provided
    - Serious violations (fraud, fake cards, harassment) are flagged for priority review
    """
    
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository
    
    async def execute(
        self,
        reporter_id: str,
        reported_user_id: str,
        reason: ReportReason,
        detail: Optional[str] = None
    ) -> Report:
        """
        Create a report against a user
        
        Args:
            reporter_id: ID of user filing the report
            reported_user_id: ID of user being reported
            reason: Reason for the report
            detail: Optional detailed explanation (max 2000 chars)
            
        Returns:
            Created Report entity
            
        Raises:
            ValueError: If validation fails
        """
        # Create report (validation happens in entity)
        report = Report(
            id=str(uuid.uuid4()),
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            detail=detail,
            created_at=datetime.utcnow(),
            resolved=False
        )
        
        return await self.report_repository.create(report)
