"""
SQLAlchemy Report Repository Implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.domain.entities.report import Report, ReportReason
from app.modules.social.domain.repositories.i_report_repository import IReportRepository
from app.modules.social.infrastructure.database.models.report_model import ReportModel


class ReportRepositoryImpl(IReportRepository):
    """SQLAlchemy implementation of Report repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, report: Report) -> Report:
        """Create a new report"""
        model = ReportModel(
            id=UUID(report.id) if isinstance(report.id, str) else report.id,
            reporter_id=UUID(report.reporter_id)
            if isinstance(report.reporter_id, str)
            else report.reporter_id,
            reported_user_id=UUID(report.reported_user_id)
            if isinstance(report.reported_user_id, str)
            else report.reported_user_id,
            reason=report.reason.value
            if isinstance(report.reason, ReportReason)
            else report.reason,
            detail=report.detail,
            created_at=report.created_at,
            resolved=report.resolved,
            resolved_at=report.resolved_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        result = await self.session.execute(
            select(ReportModel).where(ReportModel.id == UUID(report_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_reports_by_reported_user_id(
        self, reported_user_id: str, resolved: Optional[bool] = None
    ) -> List[Report]:
        """Get all reports for a specific user, optionally filtered by resolution status"""
        user_uuid = (
            UUID(reported_user_id)
            if isinstance(reported_user_id, str)
            else reported_user_id
        )

        query = select(ReportModel).where(ReportModel.reported_user_id == user_uuid)

        if resolved is not None:
            query = query.where(ReportModel.resolved == resolved)

        query = query.order_by(ReportModel.created_at.desc())

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_reports_by_reporter_id(self, reporter_id: str) -> List[Report]:
        """Get all reports filed by a specific user"""
        reporter_uuid = (
            UUID(reporter_id) if isinstance(reporter_id, str) else reporter_id
        )

        result = await self.session.execute(
            select(ReportModel)
            .where(ReportModel.reporter_id == reporter_uuid)
            .order_by(ReportModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_unresolved_reports(self, limit: int = 100) -> List[Report]:
        """Get unresolved reports for admin review"""
        result = await self.session.execute(
            select(ReportModel)
            .where(ReportModel.resolved == False)
            .order_by(ReportModel.created_at.asc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, report: Report) -> Report:
        """Update an existing report"""
        result = await self.session.execute(
            select(ReportModel).where(
                ReportModel.id
                == (UUID(report.id) if isinstance(report.id, str) else report.id)
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Report with id {report.id} not found")

        model.resolved = report.resolved
        model.resolved_at = report.resolved_at

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_report_count_by_user(
        self, reported_user_id: str, reason: Optional[ReportReason] = None
    ) -> int:
        """Get count of reports against a user, optionally filtered by reason"""
        user_uuid = (
            UUID(reported_user_id)
            if isinstance(reported_user_id, str)
            else reported_user_id
        )

        query = select(func.count(ReportModel.id)).where(
            ReportModel.reported_user_id == user_uuid
        )

        if reason:
            reason_value = reason.value if isinstance(reason, ReportReason) else reason
            query = query.where(ReportModel.reason == reason_value)

        result = await self.session.execute(query)
        count = result.scalar_one()
        return count or 0

    async def delete(self, report_id: str) -> None:
        """Delete a report"""
        result = await self.session.execute(
            select(ReportModel).where(ReportModel.id == UUID(report_id))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    @staticmethod
    def _to_entity(model: ReportModel) -> Report:
        """Convert ORM model to domain entity"""
        return Report(
            id=str(model.id),
            reporter_id=str(model.reporter_id),
            reported_user_id=str(model.reported_user_id),
            reason=ReportReason(model.reason),
            detail=model.detail,
            created_at=model.created_at,
            resolved=model.resolved,
            resolved_at=model.resolved_at,
        )


# Alias for consistency
ReportRepositoryImpl = ReportRepositoryImpl
