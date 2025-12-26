"""make rating trade_id nullable for friendship-based ratings

Revision ID: 009
Revises: 008
Create Date: 2025-12-22 04:35:00.000000

Update ratings table to support FR-SOCIAL-003A:
- Make trade_id nullable to allow friendship-based ratings
- Update indexes to support both trade-based and friendship-based ratings
- Remove unique constraint on (trade_id, rater_id) to prepare for partial unique index

Phase 6 (FR-SOCIAL-003A): Basic rating ability
- Can rate if friends OR provide trade_id
- trade_id is optional

Phase 7 (FR-SOCIAL-003B): Will add validation for completed trades
- When trade_id provided, must be completed trade
- One rating per completed trade participant
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make trade_id nullable in ratings table."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Check if ratings table exists
    tables = inspector.get_table_names()
    if "ratings" not in tables:
        raise Exception("ratings table does not exist. Run migration 008 first.")

    # 1. Drop existing unique constraint on (trade_id, rater_id) if it exists
    indexes = [idx["name"] for idx in inspector.get_indexes("ratings")]
    constraints = [c["name"] for c in inspector.get_unique_constraints("ratings")]

    if "idx_rating_trade_rater" in indexes:
        op.drop_index("idx_rating_trade_rater", table_name="ratings")

    # Drop unique constraint if exists (might be named differently)
    for constraint_name in constraints:
        if "trade" in constraint_name and "rater" in constraint_name:
            op.drop_constraint(constraint_name, "ratings", type_="unique")

    # 2. Make trade_id nullable
    op.alter_column(
        "ratings", "trade_id", existing_type=postgresql.UUID(), nullable=True
    )

    # 3. Recreate non-unique index for (trade_id, rater_id) - for trade-based rating lookup
    op.create_index("idx_rating_trade_rater", "ratings", ["trade_id", "rater_id"])

    # 4. Add new index for friendship-based ratings (rater_id, rated_user_id)
    if "idx_rating_friendship" not in indexes:
        op.create_index(
            "idx_rating_friendship", "ratings", ["rater_id", "rated_user_id"]
        )

    # Note: PostgreSQL partial unique index for trade-based ratings will be:
    # CREATE UNIQUE INDEX idx_rating_trade_rater_unique ON ratings (trade_id, rater_id) WHERE trade_id IS NOT NULL;
    # This ensures one rating per trade participant, while allowing multiple friendship ratings
    # We'll add this in application logic for now, as SQLAlchemy doesn't support partial indexes directly


def downgrade() -> None:
    """Revert trade_id back to NOT NULL."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Check if ratings table exists
    tables = inspector.get_table_names()
    if "ratings" not in tables:
        return  # Nothing to downgrade

    indexes = [idx["name"] for idx in inspector.get_indexes("ratings")]

    # 1. Remove friendship index
    if "idx_rating_friendship" in indexes:
        op.drop_index("idx_rating_friendship", table_name="ratings")

    # 2. Drop non-unique index
    if "idx_rating_trade_rater" in indexes:
        op.drop_index("idx_rating_trade_rater", table_name="ratings")

    # 3. Make trade_id NOT NULL again (this will fail if there are NULL values)
    op.alter_column(
        "ratings", "trade_id", existing_type=postgresql.UUID(), nullable=False
    )

    # 4. Recreate unique constraint
    op.create_index(
        "idx_rating_trade_rater", "ratings", ["trade_id", "rater_id"], unique=True
    )
