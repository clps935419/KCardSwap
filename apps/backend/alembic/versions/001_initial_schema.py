"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-12-15 02:50:00.000000

This migration creates all initial database tables from infra/db/init.sql.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create all initial tables: users, profiles, subscriptions, refresh_tokens, cards
    """

    # Users table
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("google_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("google_id"),
        sa.UniqueConstraint("email"),
    )

    # Profiles table
    op.create_table(
        "profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nickname", sa.String(length=100), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column(
            "preferences", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "privacy_flags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text(
                '\'{"nearby_visible": true, "show_online": true, "allow_stranger_chat": true}\'::jsonb'
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    # Subscriptions table
    op.create_table(
        "subscriptions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan", sa.String(length=50), server_default="free", nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "status", sa.String(length=50), server_default="inactive", nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Refresh Tokens table
    op.create_table(
        "refresh_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(length=500), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default="false", nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )

    # Cards table
    op.create_table(
        "cards",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idol", sa.String(length=100), nullable=True),
        sa.Column("idol_group", sa.String(length=100), nullable=True),
        sa.Column("album", sa.String(length=100), nullable=True),
        sa.Column("version", sa.String(length=100), nullable=True),
        sa.Column("rarity", sa.String(length=50), nullable=True),
        sa.Column(
            "status", sa.String(length=50), server_default="available", nullable=False
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("thumb_url", sa.Text(), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create function for updating updated_at timestamp
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """
    )

    # Create triggers for updated_at
    op.execute(
        """
        CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    )

    op.execute(
        """
        CREATE TRIGGER update_profiles_updated_at
        BEFORE UPDATE ON profiles
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    )

    op.execute(
        """
        CREATE TRIGGER update_cards_updated_at
        BEFORE UPDATE ON cards
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    )

    op.execute(
        """
        CREATE TRIGGER update_subscriptions_updated_at
        BEFORE UPDATE ON subscriptions
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    )

    op.execute(
        """
        CREATE TRIGGER update_refresh_tokens_updated_at
        BEFORE UPDATE ON refresh_tokens
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    )


def downgrade() -> None:
    """
    Drop all tables and triggers created in upgrade
    """

    # Drop triggers
    op.execute(
        "DROP TRIGGER IF EXISTS update_refresh_tokens_updated_at ON refresh_tokens"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions"
    )
    op.execute("DROP TRIGGER IF EXISTS update_cards_updated_at ON cards")
    op.execute("DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles")
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables (in reverse order of creation, respecting foreign keys)
    op.drop_table("cards")
    op.drop_table("refresh_tokens")
    op.drop_table("subscriptions")
    op.drop_table("profiles")
    op.drop_table("users")
