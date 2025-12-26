"""
Report Repository Interface

Domain layer repository interface - defines contract for report persistence
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.social.domain.entities.report import Report, ReportReason


class IReportRepository(ABC):
    """Repository interface for Report entity persistence"""

    @abstractmethod
    async def create(self, report: Report) -> Report:
        """Create a new report"""
        pass

    @abstractmethod
    async def get_by_id(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        pass

    @abstractmethod
    async def get_reports_by_reported_user_id(
        self,
        reported_user_id: str,
        resolved: Optional[bool] = None
    ) -> List[Report]:
        """Get all reports for a specific user, optionally filtered by resolution status"""
        pass

    @abstractmethod
    async def get_reports_by_reporter_id(self, reporter_id: str) -> List[Report]:
        """Get all reports filed by a specific user"""
        pass

    @abstractmethod
    async def get_unresolved_reports(self, limit: int = 100) -> List[Report]:
        """Get unresolved reports for admin review"""
        pass

    @abstractmethod
    async def update(self, report: Report) -> Report:
        """Update an existing report"""
        pass

    @abstractmethod
    async def get_report_count_by_user(
        self,
        reported_user_id: str,
        reason: Optional[ReportReason] = None
    ) -> int:
        """Get count of reports against a user, optionally filtered by reason"""
        pass

    @abstractmethod
    async def delete(self, report_id: str) -> None:
        """Delete a report"""
        pass
