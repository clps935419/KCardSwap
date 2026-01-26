"""add card upload confirmation fields

Revision ID: 013_add_card_upload_confirmation
Revises: 012
Create Date: 2025-12-29 04:30:00.000000

Add upload_status and upload_confirmed_at fields to cards table
to support upload confirmation flow and avoid ghost records.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "013_add_card_upload_confirmation"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add upload_status and upload_confirmed_at fields to cards table."""

    # Check if cards table exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    if "cards" not in tables:
        raise RuntimeError(
            "cards table does not exist. Please run migration 005 first."
        )

    # Get existing columns
    columns = [col["name"] for col in inspector.get_columns("cards")]

    # Add upload_status column if it doesn't exist
    if "upload_status" not in columns:
        op.add_column(
            "cards",
            sa.Column(
                "upload_status",
                sa.String(length=50),
                nullable=False,
                server_default="pending",
            ),
        )

    # Add upload_confirmed_at column if it doesn't exist
    if "upload_confirmed_at" not in columns:
        op.add_column(
            "cards",
            sa.Column(
                "upload_confirmed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    # Create index on upload_status if it doesn't exist
    indexes = [idx["name"] for idx in inspector.get_indexes("cards")]
    if "idx_cards_upload_status" not in indexes:
        op.create_index("idx_cards_upload_status", "cards", ["upload_status"])


def downgrade() -> None:
    """Remove upload_status and upload_confirmed_at fields from cards table."""

    # Check if cards table exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    if "cards" not in tables:
        return  # Nothing to downgrade if table doesn't exist

    # Get existing columns and indexes
    columns = [col["name"] for col in inspector.get_columns("cards")]
    indexes = [idx["name"] for idx in inspector.get_indexes("cards")]

    # Drop index if it exists
    if "idx_cards_upload_status" in indexes:
        op.drop_index("idx_cards_upload_status", "cards")

    # Drop columns if they exist
    if "upload_confirmed_at" in columns:
        op.drop_column("cards", "upload_confirmed_at")

    if "upload_status" in columns:
        op.drop_column("cards", "upload_status")
