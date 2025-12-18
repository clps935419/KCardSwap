"""add id field to profiles table

Revision ID: 004
Revises: 003
Create Date: 2025-12-18 07:00:00.000000

Add id field as primary key to profiles table, making user_id a unique foreign key instead.
This aligns with the project standard that all tables should have an id field.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add id column to profiles table and make user_id unique."""
    
    # Step 1: Drop the existing primary key constraint on user_id
    op.execute('ALTER TABLE profiles DROP CONSTRAINT profiles_pkey')
    
    # Step 2: Add the new id column with UUID type and default value
    op.add_column('profiles', sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')))
    
    # Step 3: Create primary key constraint on the new id column
    op.create_primary_key('profiles_pkey', 'profiles', ['id'])
    
    # Step 4: Create unique constraint on user_id
    op.create_unique_constraint('uq_profiles_user_id', 'profiles', ['user_id'])
    
    # Step 5: Create index on user_id for faster lookups
    op.create_index('idx_profiles_user_id', 'profiles', ['user_id'])


def downgrade() -> None:
    """Revert profiles table to use user_id as primary key."""
    
    # Step 1: Drop the index on user_id
    op.drop_index('idx_profiles_user_id', 'profiles')
    
    # Step 2: Drop the unique constraint on user_id
    op.drop_constraint('uq_profiles_user_id', 'profiles', type_='unique')
    
    # Step 3: Drop the primary key constraint on id
    op.drop_constraint('profiles_pkey', 'profiles', type_='primary')
    
    # Step 4: Drop the id column
    op.drop_column('profiles', 'id')
    
    # Step 5: Recreate primary key constraint on user_id
    op.create_primary_key('profiles_pkey', 'profiles', ['user_id'])
