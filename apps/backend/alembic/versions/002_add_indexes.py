"""add indexes

Revision ID: 002
Revises: 001
Create Date: 2025-12-15 02:50:10.000000

This migration creates all indexes from infra/db/init.sql for better query performance.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create indexes for better query performance
    """
    
    # Users indexes
    op.create_index('idx_users_google_id', 'users', ['google_id'], unique=False)
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    
    # Cards indexes
    op.create_index('idx_cards_owner_id', 'cards', ['owner_id'], unique=False)
    op.create_index('idx_cards_status', 'cards', ['status'], unique=False)
    
    # Subscriptions indexes
    op.create_index('idx_subscriptions_user_id', 'subscriptions', ['user_id'], unique=False)
    
    # Refresh Tokens indexes
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'], unique=False)
    op.create_index('idx_refresh_tokens_token', 'refresh_tokens', ['token'], unique=False)


def downgrade() -> None:
    """
    Drop all indexes created in upgrade
    """
    
    # Drop in reverse order
    op.drop_index('idx_refresh_tokens_token', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_index('idx_subscriptions_user_id', table_name='subscriptions')
    op.drop_index('idx_cards_status', table_name='cards')
    op.drop_index('idx_cards_owner_id', table_name='cards')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_users_google_id', table_name='users')
