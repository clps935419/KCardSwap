"""Add message threads and requests tables

Revision ID: 018_add_message_threads
Revises: 017_add_media_relationships
Create Date: 2024-01-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '018_add_message_threads'
down_revision = '017_add_media_relationships'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add message_threads, message_requests, and thread_messages tables for User Story 5."""
    
    # Create message_threads table
    op.create_table(
        'message_threads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_a_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_b_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Add foreign keys for message_threads
    op.create_foreign_key(
        'fk_message_threads_user_a',
        'message_threads',
        'users',
        ['user_a_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_message_threads_user_b',
        'message_threads',
        'users',
        ['user_b_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Add indexes for message_threads
    op.create_index('idx_thread_user_a', 'message_threads', ['user_a_id'])
    op.create_index('idx_thread_user_b', 'message_threads', ['user_b_id'])
    op.create_index('idx_thread_last_message', 'message_threads', ['last_message_at'])
    
    # Add unique constraint for user pair (FR-014: one thread per user pair)
    op.create_unique_constraint('uq_thread_users', 'message_threads', ['user_a_id', 'user_b_id'])
    
    # Create message_requests table
    op.create_table(
        'message_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('initial_message', sa.Text, nullable=False),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('thread_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Add foreign keys for message_requests
    op.create_foreign_key(
        'fk_message_requests_sender',
        'message_requests',
        'users',
        ['sender_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_message_requests_recipient',
        'message_requests',
        'users',
        ['recipient_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_message_requests_post',
        'message_requests',
        'posts',
        ['post_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_message_requests_thread',
        'message_requests',
        'message_threads',
        ['thread_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Add indexes for message_requests
    op.create_index('idx_message_request_recipient_status', 'message_requests', ['recipient_id', 'status'])
    op.create_index('idx_message_request_users', 'message_requests', ['sender_id', 'recipient_id'])
    
    # Create thread_messages table
    op.create_table(
        'thread_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('thread_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # Add foreign keys for thread_messages
    op.create_foreign_key(
        'fk_thread_messages_thread',
        'thread_messages',
        'message_threads',
        ['thread_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_thread_messages_sender',
        'thread_messages',
        'users',
        ['sender_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_thread_messages_post',
        'thread_messages',
        'posts',
        ['post_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Add indexes for thread_messages
    op.create_index('idx_thread_message_thread_created', 'thread_messages', ['thread_id', 'created_at'])


def downgrade() -> None:
    """Remove message threads and requests tables."""
    # Drop thread_messages
    op.drop_index('idx_thread_message_thread_created', table_name='thread_messages')
    op.drop_constraint('fk_thread_messages_post', 'thread_messages', type_='foreignkey')
    op.drop_constraint('fk_thread_messages_sender', 'thread_messages', type_='foreignkey')
    op.drop_constraint('fk_thread_messages_thread', 'thread_messages', type_='foreignkey')
    op.drop_table('thread_messages')
    
    # Drop message_requests
    op.drop_index('idx_message_request_users', table_name='message_requests')
    op.drop_index('idx_message_request_recipient_status', table_name='message_requests')
    op.drop_constraint('fk_message_requests_thread', 'message_requests', type_='foreignkey')
    op.drop_constraint('fk_message_requests_post', 'message_requests', type_='foreignkey')
    op.drop_constraint('fk_message_requests_recipient', 'message_requests', type_='foreignkey')
    op.drop_constraint('fk_message_requests_sender', 'message_requests', type_='foreignkey')
    op.drop_table('message_requests')
    
    # Drop message_threads
    op.drop_constraint('uq_thread_users', 'message_threads', type_='unique')
    op.drop_index('idx_thread_last_message', table_name='message_threads')
    op.drop_index('idx_thread_user_b', table_name='message_threads')
    op.drop_index('idx_thread_user_a', table_name='message_threads')
    op.drop_constraint('fk_message_threads_user_b', 'message_threads', type_='foreignkey')
    op.drop_constraint('fk_message_threads_user_a', 'message_threads', type_='foreignkey')
    op.drop_table('message_threads')
