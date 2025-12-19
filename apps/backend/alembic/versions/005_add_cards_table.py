"""add cards table for Phase 4 User Story 2

Revision ID: 005
Revises: 004
Create Date: 2025-12-19 04:32:00.000000

Add cards table for card upload and management feature.
Includes fields for owner, idol info, image URL, size, and status tracking.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create cards table."""
    
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
    
    # Create indexes for better query performance
    op.create_index('idx_cards_owner_id', 'cards', ['owner_id'])
    op.create_index('idx_cards_status', 'cards', ['status'])
    op.create_index('idx_cards_created_at', 'cards', ['created_at'])
    
    # Create trigger for automatic updated_at
    op.execute("""
        CREATE TRIGGER update_cards_updated_at
        BEFORE UPDATE ON cards
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop cards table."""
    
    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS update_cards_updated_at ON cards;")
    
    # Drop indexes
    op.drop_index('idx_cards_created_at', 'cards')
    op.drop_index('idx_cards_status', 'cards')
    op.drop_index('idx_cards_owner_id', 'cards')
    
    # Drop table
    op.drop_table('cards')
