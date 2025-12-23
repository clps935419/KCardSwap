"""Add subscription and purchase token tables

Revision ID: 011
Revises: 010
Create Date: 2025-12-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create subscriptions and subscription_purchase_tokens tables.

    subscriptions: Tracks user subscription plans and status
    subscription_purchase_tokens: Tracks purchase tokens to prevent replay attacks
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    # Create subscriptions table if missing (idempotent for reruns)
    if "subscriptions" not in tables:
        op.create_table(
            "subscriptions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column(
                "plan", sa.String(length=20), nullable=False, server_default="free"
            ),
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="inactive",
            ),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )

    subscription_indexes = (
        [idx["name"] for idx in inspector.get_indexes("subscriptions")]
        if "subscriptions" in tables
        else []
    )
    if "ix_subscriptions_id" not in subscription_indexes and "subscriptions" in tables:
        op.create_index("ix_subscriptions_id", "subscriptions", ["id"])
    if (
        "ix_subscriptions_user_id" not in subscription_indexes
        and "subscriptions" in tables
    ):
        op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    if (
        "ix_subscriptions_status_expires_at" not in subscription_indexes
        and "subscriptions" in tables
    ):
        op.create_index(
            "ix_subscriptions_status_expires_at",
            "subscriptions",
            ["status", "expires_at"],
        )

    # Create subscription_purchase_tokens table if missing (idempotent for reruns)
    if "subscription_purchase_tokens" not in tables:
        op.create_table(
            "subscription_purchase_tokens",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("purchase_token", sa.String(length=1000), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("product_id", sa.String(length=100), nullable=False),
            sa.Column(
                "platform",
                sa.String(length=20),
                nullable=False,
                server_default="android",
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("purchase_token"),
        )

    token_indexes = (
        [idx["name"] for idx in inspector.get_indexes("subscription_purchase_tokens")]
        if "subscription_purchase_tokens" in tables
        else []
    )
    if (
        "ix_purchase_tokens_token" not in token_indexes
        and "subscription_purchase_tokens" in tables
    ):
        op.create_index(
            "ix_purchase_tokens_token",
            "subscription_purchase_tokens",
            ["purchase_token"],
        )
    if (
        "ix_purchase_tokens_user_id" not in token_indexes
        and "subscription_purchase_tokens" in tables
    ):
        op.create_index(
            "ix_purchase_tokens_user_id", "subscription_purchase_tokens", ["user_id"]
        )


def downgrade() -> None:
    """Drop subscription and purchase token tables"""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    if "subscription_purchase_tokens" in tables:
        token_indexes = [
            idx["name"] for idx in inspector.get_indexes("subscription_purchase_tokens")
        ]
        if "ix_purchase_tokens_user_id" in token_indexes:
            op.drop_index(
                "ix_purchase_tokens_user_id", table_name="subscription_purchase_tokens"
            )
        if "ix_purchase_tokens_token" in token_indexes:
            op.drop_index(
                "ix_purchase_tokens_token", table_name="subscription_purchase_tokens"
            )
        op.drop_table("subscription_purchase_tokens")

    if "subscriptions" in tables:
        subscription_indexes = [
            idx["name"] for idx in inspector.get_indexes("subscriptions")
        ]
        if "ix_subscriptions_status_expires_at" in subscription_indexes:
            op.drop_index(
                "ix_subscriptions_status_expires_at", table_name="subscriptions"
            )
        if "ix_subscriptions_user_id" in subscription_indexes:
            op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
        if "ix_subscriptions_id" in subscription_indexes:
            op.drop_index("ix_subscriptions_id", table_name="subscriptions")
        op.drop_table("subscriptions")
