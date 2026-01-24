"""Add post_likes table for User Story 4

Revision ID: 019_add_post_likes
Revises: 018_add_message_threads
Create Date: 2024-01-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '019_add_post_likes'
down_revision = '018_add_message_threads'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add post_likes table for FR-008 and FR-009."""
    op.create_table(
        'post_likes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('post_id', 'user_id', name='uq_post_likes_post_user'),
    )
    
    # Add indexes for efficient queries
    op.create_index('ix_post_likes_post_id', 'post_likes', ['post_id'])
    op.create_index('ix_post_likes_user_id', 'post_likes', ['user_id'])


def downgrade() -> None:
    """Drop post_likes table."""
    op.drop_index('ix_post_likes_user_id', table_name='post_likes')
    op.drop_index('ix_post_likes_post_id', table_name='post_likes')
    op.drop_table('post_likes')
