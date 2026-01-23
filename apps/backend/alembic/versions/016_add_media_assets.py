"""Add media_assets table

Revision ID: 016_add_media_assets
Revises: 015_add_gallery_cards
Create Date: 2024-01-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '016_add_media_assets'
down_revision = '015_add_gallery_cards'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add media_assets table for User Story 3 media upload flow."""
    op.create_table(
        'media_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('gcs_blob_name', sa.String(500), nullable=False, unique=True),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Add indexes for efficient queries
    op.create_index('idx_media_assets_owner_id', 'media_assets', ['owner_id'])
    op.create_index('idx_media_assets_status', 'media_assets', ['status'])


def downgrade() -> None:
    """Remove media_assets table."""
    op.drop_index('idx_media_assets_status', table_name='media_assets')
    op.drop_index('idx_media_assets_owner_id', table_name='media_assets')
    op.drop_table('media_assets')
