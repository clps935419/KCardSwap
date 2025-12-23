"""Add subscription and purchase token tables

Revision ID: 011_add_subscription_tables
Revises: 010_add_trade_tables
Create Date: 2025-12-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '011_add_subscription_tables'
down_revision: Union[str, None] = '010_add_trade_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create subscriptions and subscription_purchase_tokens tables.
    
    subscriptions: Tracks user subscription plans and status
    subscription_purchase_tokens: Tracks purchase tokens to prevent replay attacks
    """
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan', sa.String(length=20), nullable=False, server_default='free'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='inactive'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create indexes for subscriptions
    op.create_index('ix_subscriptions_id', 'subscriptions', ['id'])
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_status_expires_at', 'subscriptions', ['status', 'expires_at'])
    
    # Create subscription_purchase_tokens table
    op.create_table(
        'subscription_purchase_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('purchase_token', sa.String(length=1000), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', sa.String(length=100), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False, server_default='android'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('purchase_token')
    )
    
    # Create indexes for subscription_purchase_tokens
    op.create_index('ix_purchase_tokens_token', 'subscription_purchase_tokens', ['purchase_token'])
    op.create_index('ix_purchase_tokens_user_id', 'subscription_purchase_tokens', ['user_id'])


def downgrade() -> None:
    """Drop subscription and purchase token tables"""
    # Drop indexes first
    op.drop_index('ix_purchase_tokens_user_id', table_name='subscription_purchase_tokens')
    op.drop_index('ix_purchase_tokens_token', table_name='subscription_purchase_tokens')
    op.drop_index('ix_subscriptions_status_expires_at', table_name='subscriptions')
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_id', table_name='subscriptions')
    
    # Drop tables
    op.drop_table('subscription_purchase_tokens')
    op.drop_table('subscriptions')
