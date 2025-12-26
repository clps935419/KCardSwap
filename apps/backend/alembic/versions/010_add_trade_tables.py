"""add Phase 7 tables for trade system

Revision ID: 010
Revises: 009
Create Date: 2025-12-22 08:00:00.000000

Add tables for Phase 7 User Story 5: Trade System
- trades: trade proposals and status tracking
- trade_items: cards being exchanged in each trade
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Phase 7 tables (idempotent)."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    # 1. Create trades table
    if 'trades' not in tables:
        op.create_table(
            'trades',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
            sa.Column('initiator_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('responder_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='proposed'),
            sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('initiator_confirmed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('responder_confirmed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

            # Foreign key constraints
            sa.ForeignKeyConstraint(['initiator_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['responder_id'], ['users.id'], ondelete='CASCADE'),
        )

        # Create trigger for automatic updated_at
        op.execute("""
            CREATE TRIGGER update_trades_updated_at
            BEFORE UPDATE ON trades
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)

    # Create indexes for trades
    indexes = [idx['name'] for idx in inspector.get_indexes('trades')] if 'trades' in tables else []

    if 'idx_trades_initiator_id' not in indexes:
        op.create_index('idx_trades_initiator_id', 'trades', ['initiator_id'])

    if 'idx_trades_responder_id' not in indexes:
        op.create_index('idx_trades_responder_id', 'trades', ['responder_id'])

    if 'idx_trades_status' not in indexes:
        op.create_index('idx_trades_status', 'trades', ['status'])

    if 'idx_trades_initiator_created' not in indexes:
        op.create_index('idx_trades_initiator_created', 'trades', ['initiator_id', 'created_at'])

    if 'idx_trades_responder_created' not in indexes:
        op.create_index('idx_trades_responder_created', 'trades', ['responder_id', 'created_at'])

    if 'idx_trades_status_created' not in indexes:
        op.create_index('idx_trades_status_created', 'trades', ['status', 'created_at'])

    # 2. Create trade_items table
    if 'trade_items' not in tables:
        op.create_table(
            'trade_items',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
            sa.Column('trade_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('card_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('owner_side', sa.String(length=20), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

            # Foreign key constraints
            sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),

            # Unique constraint: no duplicate cards in same trade
            sa.UniqueConstraint('trade_id', 'card_id', name='uq_trade_card'),
        )

    # Create indexes for trade_items
    item_indexes = [idx['name'] for idx in inspector.get_indexes('trade_items')] if 'trade_items' in tables else []

    if 'idx_trade_items_trade_id' not in item_indexes:
        op.create_index('idx_trade_items_trade_id', 'trade_items', ['trade_id'])

    if 'idx_trade_items_card_id' not in item_indexes:
        op.create_index('idx_trade_items_card_id', 'trade_items', ['card_id'])


def downgrade() -> None:
    """Drop Phase 7 tables."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    # Drop trade_items table and its indexes
    if 'trade_items' in tables:
        op.drop_index('idx_trade_items_card_id', table_name='trade_items', if_exists=True)
        op.drop_index('idx_trade_items_trade_id', table_name='trade_items', if_exists=True)
        op.drop_table('trade_items')

    # Drop trades table and its indexes
    if 'trades' in tables:
        op.execute("DROP TRIGGER IF EXISTS update_trades_updated_at ON trades;")
        op.drop_index('idx_trades_status_created', table_name='trades', if_exists=True)
        op.drop_index('idx_trades_responder_created', table_name='trades', if_exists=True)
        op.drop_index('idx_trades_initiator_created', table_name='trades', if_exists=True)
        op.drop_index('idx_trades_status', table_name='trades', if_exists=True)
        op.drop_index('idx_trades_responder_id', table_name='trades', if_exists=True)
        op.drop_index('idx_trades_initiator_id', table_name='trades', if_exists=True)
        op.drop_table('trades')
