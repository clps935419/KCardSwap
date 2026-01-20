"""add location and stealth mode to profiles for Phase 5 US3

Revision ID: 006
Revises: 005
Create Date: 2025-12-19 10:30:00.000000

Add last_lat, last_lng, and stealth_mode fields to profiles table
for nearby card search functionality.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add location and stealth mode fields to profiles."""

    # Add last_lat field (user's last known latitude)
    op.add_column(
        "profiles",
        sa.Column("last_lat", sa.Float, nullable=True, comment="Last known latitude"),
    )

    # Add last_lng field (user's last known longitude)
    op.add_column(
        "profiles",
        sa.Column("last_lng", sa.Float, nullable=True, comment="Last known longitude"),
    )

    # Add stealth_mode field (hide from nearby search)
    op.add_column(
        "profiles",
        sa.Column(
            "stealth_mode",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Hide from nearby search",
        ),
    )

    # Create index on stealth_mode for efficient filtering
    op.create_index("idx_profiles_stealth_mode", "profiles", ["stealth_mode"])


def downgrade() -> None:
    """Remove location and stealth mode fields from profiles (idempotent)."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    if "profiles" not in tables:
        return  # Nothing to downgrade

    indexes = [idx["name"] for idx in inspector.get_indexes("profiles")]
    columns = [col["name"] for col in inspector.get_columns("profiles")]

    # Drop index if it exists
    if "idx_profiles_stealth_mode" in indexes:
        op.drop_index("idx_profiles_stealth_mode", table_name="profiles")

    # Drop columns if they exist
    if "stealth_mode" in columns:
        op.drop_column("profiles", "stealth_mode")
    if "last_lng" in columns:
        op.drop_column("profiles", "last_lng")
    if "last_lat" in columns:
        op.drop_column("profiles", "last_lat")
