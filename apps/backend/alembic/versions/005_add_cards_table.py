"""add cards table for Phase 4 User Story 2

Revision ID: 005
Revises: 004
Create Date: 2025-12-19 04:32:00.000000

Add cards table for card upload and management feature.
Includes fields for owner, idol info, image URL, size, and status tracking.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create cards table if it doesn't exist (idempotent for existing installations)."""

    # Check if cards table already exists (from migration 001)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    if 'cards' not in tables:
        # Table doesn't exist, create it
        op.create_table(
            'cards',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
            sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('idol', sa.String(length=100), nullable=True),
            sa.Column('idol_group', sa.String(length=100), nullable=True),
            sa.Column('album', sa.String(length=100), nullable=True),
            sa.Column('version', sa.String(length=100), nullable=True),
            sa.Column('rarity', sa.String(length=50), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=False, server_default='available'),
            sa.Column('image_url', sa.Text(), nullable=True),
            sa.Column('size_bytes', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

            # Foreign key constraint
            sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        )

        # Create trigger for automatic updated_at
        op.execute("""
            CREATE TRIGGER update_cards_updated_at
            BEFORE UPDATE ON cards
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)

    # Create indexes if they don't exist (idempotent)
    indexes = [idx['name'] for idx in inspector.get_indexes('cards')] if 'cards' in tables else []

    if 'idx_cards_owner_id' not in indexes:
        op.create_index('idx_cards_owner_id', 'cards', ['owner_id'])

    if 'idx_cards_status' not in indexes:
        op.create_index('idx_cards_status', 'cards', ['status'])

    if 'idx_cards_created_at' not in indexes:
        op.create_index('idx_cards_created_at', 'cards', ['created_at'])


def downgrade() -> None:
    """Drop cards table (idempotent)."""

    # Check if cards table exists before attempting to drop
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    if 'cards' in tables:
        # Drop trigger first if it exists
        op.execute("DROP TRIGGER IF EXISTS update_cards_updated_at ON cards;")

        # Drop indexes if they exist
        indexes = [idx['name'] for idx in inspector.get_indexes('cards')]

        if 'idx_cards_created_at' in indexes:
            op.drop_index('idx_cards_created_at', 'cards')

        if 'idx_cards_status' in indexes:
            op.drop_index('idx_cards_status', 'cards')

        if 'idx_cards_owner_id' in indexes:
            op.drop_index('idx_cards_owner_id', 'cards')

        # Drop table
        op.drop_table('cards')
