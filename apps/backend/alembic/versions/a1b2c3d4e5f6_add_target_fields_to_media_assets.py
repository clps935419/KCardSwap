"""add_target_fields_to_media_assets

Revision ID: a1b2c3d4e5f6
Revises: 13c0ed406266
Create Date: 2026-02-05 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '13c0ed406266'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add target_type and target_id columns to media_assets table.
    
    Phase 9: Support tracking which post/gallery_card a media is attached to.
    """
    # Add target_type column (nullable for backward compatibility)
    op.add_column('media_assets', sa.Column('target_type', sa.String(length=50), nullable=True))
    
    # Add target_id column (nullable for backward compatibility)
    op.add_column('media_assets', sa.Column('target_id', sa.UUID(), nullable=True))
    
    # Add index for efficient queries by target
    op.create_index(
        op.f('ix_media_assets_target_type_target_id'),
        'media_assets',
        ['target_type', 'target_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove target fields from media_assets table."""
    op.drop_index(op.f('ix_media_assets_target_type_target_id'), table_name='media_assets')
    op.drop_column('media_assets', 'target_id')
    op.drop_column('media_assets', 'target_type')
