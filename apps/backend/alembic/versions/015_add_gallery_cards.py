"""Add gallery_cards table for User Story 2

Revision ID: 015_add_gallery_cards
Revises: 014_add_posts_scope_category
Create Date: 2026-01-23

FR-017, FR-018, FR-019: Personal gallery cards with display ordering
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "015_add_gallery_cards"
down_revision: Union[str, None] = "014_add_posts_scope_category"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create gallery_cards table"""
    
    op.create_table(
        'gallery_cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('idol_name', sa.String(100), nullable=False),
        sa.Column('era', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('media_asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_gallery_cards_user_id'),
    )
    
    # Create indexes for efficient queries
    op.create_index('idx_gallery_cards_user_id', 'gallery_cards', ['user_id'])
    op.create_index('idx_gallery_cards_user_id_display_order', 'gallery_cards', ['user_id', 'display_order'])


def downgrade() -> None:
    """Drop gallery_cards table"""
    
    op.drop_index('idx_gallery_cards_user_id_display_order', 'gallery_cards')
    op.drop_index('idx_gallery_cards_user_id', 'gallery_cards')
    op.drop_table('gallery_cards')
