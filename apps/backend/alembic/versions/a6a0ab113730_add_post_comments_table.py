"""add post_comments table

Revision ID: a6a0ab113730
Revises: e60f43542709
Create Date: 2026-02-09 08:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a6a0ab113730'
down_revision: Union[str, Sequence[str], None] = 'e60f43542709'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create post_comments table."""
    op.create_table(
        'post_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_post_comments_post_id', 'post_comments', ['post_id'], unique=False)
    op.create_index('idx_post_comments_user_id', 'post_comments', ['user_id'], unique=False)
    op.create_index('idx_post_comments_post_id_created_at', 'post_comments', ['post_id', 'created_at'], unique=False)


def downgrade() -> None:
    """Drop post_comments table."""
    op.drop_index('idx_post_comments_post_id_created_at', table_name='post_comments')
    op.drop_index('idx_post_comments_user_id', table_name='post_comments')
    op.drop_index('idx_post_comments_post_id', table_name='post_comments')
    op.drop_table('post_comments')
