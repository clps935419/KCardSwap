"""Add media relationships to posts and gallery_cards

Revision ID: 017_add_media_relationships
Revises: 016_add_media_assets
Create Date: 2024-01-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '017_add_media_relationships'
down_revision = '016_add_media_assets'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add media_asset_id to posts and gallery_cards for User Story 3."""
    # Add media_asset_id to posts table
    op.add_column('posts', sa.Column('media_asset_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_posts_media_asset_id',
        'posts',
        'media_assets',
        ['media_asset_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index('idx_posts_media_asset_id', 'posts', ['media_asset_id'])

    # Note: gallery_cards already has media_asset_id from previous migration (015_add_gallery_cards)
    # If not, uncomment below:
    # op.add_column('gallery_cards', sa.Column('media_asset_id', postgresql.UUID(as_uuid=True), nullable=True))
    # op.create_foreign_key(
    #     'fk_gallery_cards_media_asset_id',
    #     'gallery_cards',
    #     'media_assets',
    #     ['media_asset_id'],
    #     ['id'],
    #     ondelete='SET NULL'
    # )


def downgrade() -> None:
    """Remove media relationships."""
    op.drop_index('idx_posts_media_asset_id', table_name='posts')
    op.drop_constraint('fk_posts_media_asset_id', 'posts', type_='foreignkey')
    op.drop_column('posts', 'media_asset_id')
