"""add admin fields to users

Revision ID: 003
Revises: 002
Create Date: 2025-12-17 09:56:00.000000

Add password_hash and role fields to users table for admin authentication.
Make google_id nullable to support both OAuth and password-based authentication.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password_hash and role columns to users table."""
    # Add password_hash column (nullable)
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))
    
    # Add role column with default 'user'
    op.add_column('users', sa.Column('role', sa.String(length=20), server_default='user', nullable=False))
    
    # Make google_id nullable for admin users
    op.alter_column('users', 'google_id', nullable=True)
    
    # Add check constraint to ensure either google_id or password_hash is set
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT check_auth_method 
        CHECK (google_id IS NOT NULL OR password_hash IS NOT NULL)
    """)
    
    # Add check constraint for valid role values
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT check_role_values 
        CHECK (role IN ('user', 'admin', 'super_admin'))
    """)


def downgrade() -> None:
    """Remove admin fields from users table."""
    # Drop constraints
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS check_role_values")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS check_auth_method")
    
    # Make google_id not nullable again
    op.alter_column('users', 'google_id', nullable=False)
    
    # Drop columns
    op.drop_column('users', 'role')
    op.drop_column('users', 'password_hash')
