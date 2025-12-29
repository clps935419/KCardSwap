"""add search_quotas table for Phase 5 US3

Revision ID: 007
Revises: 006
Create Date: 2025-12-19 10:35:00.000000

Add search_quotas table to track daily search counts for rate limiting.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create search_quotas table."""

    op.create_table(
        "search_quotas",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("count", sa.Integer, nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("user_id", "date"),
    )

    # Create indexes for efficient queries
    op.create_index("idx_search_quotas_user_id", "search_quotas", ["user_id"])

    op.create_index("idx_search_quotas_date", "search_quotas", ["date"])


def downgrade() -> None:
    """Drop search_quotas table."""

    op.drop_index("idx_search_quotas_date", table_name="search_quotas")
    op.drop_index("idx_search_quotas_user_id", table_name="search_quotas")
    op.drop_table("search_quotas")
