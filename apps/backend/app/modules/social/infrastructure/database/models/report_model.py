"""
Report ORM model for Social module
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

from app.shared.infrastructure.database.connection import Base


class ReportModel(Base):
    """Report ORM model"""

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reported_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reason = Column(String(100), nullable=False, index=True)
    # fraud, fake_card, harassment, inappropriate_content, spam, other
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    resolved = Column(
        Boolean, nullable=False, default=False, server_default="false", index=True
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Compound indexes for efficient querying
    __table_args__ = (
        # For admin review queries
        Index("idx_report_resolved_created", "resolved", "created_at"),
        # For getting report count by user and reason
        Index("idx_report_user_reason", "reported_user_id", "reason"),
    )
