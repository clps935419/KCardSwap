"""Add scope, category to posts table for V2

Revision ID: 014_add_posts_scope_category
Revises: 013_add_card_upload_confirmation
Create Date: 2026-01-23

FR-002, FR-003, FR-004: Add scope (global/city) and category fields to posts
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "014_add_posts_scope_category"
down_revision: Union[str, None] = "013_add_card_upload_confirmation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add scope, category to posts table; make city_code nullable"""
    
    # Add new columns
    op.add_column('posts', sa.Column('scope', sa.String(20), nullable=False, server_default='global'))
    op.add_column('posts', sa.Column('category', sa.String(20), nullable=False, server_default='trade'))
    
    # Make city_code nullable (for global posts)
    op.alter_column('posts', 'city_code', nullable=True)
    
    # Add new indexes for efficient queries
    op.create_index('idx_posts_scope_status_created_at', 'posts', ['scope', 'status', 'created_at'])
    op.create_index('idx_posts_category_status', 'posts', ['category', 'status'])
    
    # Drop old index that's no longer optimal
    op.drop_index('idx_posts_board_status_created_at', 'posts')
    
    # Create new city-specific index
    op.create_index('idx_posts_city_status_created_at', 'posts', ['city_code', 'status', 'created_at'])


def downgrade() -> None:
    """Revert changes"""
    
    # Drop new indexes
    op.drop_index('idx_posts_city_status_created_at', 'posts')
    op.drop_index('idx_posts_category_status', 'posts')
    op.drop_index('idx_posts_scope_status_created_at', 'posts')
    
    # Restore old index
    op.create_index('idx_posts_board_status_created_at', 'posts', ['city_code', 'status', 'created_at'])
    
    # Make city_code required again
    op.alter_column('posts', 'city_code', nullable=False)
    
    # Drop new columns
    op.drop_column('posts', 'category')
    op.drop_column('posts', 'scope')
