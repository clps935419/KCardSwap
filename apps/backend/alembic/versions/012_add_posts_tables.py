"""Add posts and post_interests tables

Revision ID: 012
Revises: 011
Create Date: 2025-12-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create posts and post_interests tables for city board feature.

    posts: City board posts for card exchange
    post_interests: User interests in posts
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    # Create posts table if missing
    if "posts" not in tables:
        op.create_table(
            "posts",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                nullable=False,
                server_default=sa.text("uuid_generate_v4()"),
            ),
            sa.Column(
                "owner_id",
                postgresql.UUID(as_uuid=True),
                nullable=False,
            ),
            sa.Column("city_code", sa.String(length=20), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("idol", sa.String(length=100), nullable=True),
            sa.Column("idol_group", sa.String(length=100), nullable=True),
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="open",
            ),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
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
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["owner_id"],
                ["users.id"],
                name="fk_posts_owner_id",
                ondelete="CASCADE",
            ),
        )

        # Create indexes for posts
        op.create_index(
            "idx_posts_board_status_created_at",
            "posts",
            ["city_code", "status", "created_at"],
            unique=False,
        )
        op.create_index("idx_posts_owner_id", "posts", ["owner_id"], unique=False)
        op.create_index("idx_posts_idol", "posts", ["idol"], unique=False)
        op.create_index("idx_posts_idol_group", "posts", ["idol_group"], unique=False)
        op.create_index("idx_posts_expires_at", "posts", ["expires_at"], unique=False)

    # Create post_interests table if missing
    if "post_interests" not in tables:
        op.create_table(
            "post_interests",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                nullable=False,
                server_default=sa.text("uuid_generate_v4()"),
            ),
            sa.Column(
                "post_id",
                postgresql.UUID(as_uuid=True),
                nullable=False,
            ),
            sa.Column(
                "user_id",
                postgresql.UUID(as_uuid=True),
                nullable=False,
            ),
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="pending",
            ),
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
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["post_id"],
                ["posts.id"],
                name="fk_post_interests_post_id",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="fk_post_interests_user_id",
                ondelete="CASCADE",
            ),
            sa.UniqueConstraint(
                "post_id",
                "user_id",
                name="uq_post_user_interest",
            ),
        )

        # Create indexes for post_interests
        op.create_index(
            "idx_post_interests_post_id_created_at",
            "post_interests",
            ["post_id", "created_at"],
            unique=False,
        )
        op.create_index(
            "idx_post_interests_user_id_created_at",
            "post_interests",
            ["user_id", "created_at"],
            unique=False,
        )


def downgrade() -> None:
    """Drop posts and post_interests tables"""
    # Drop in reverse order (child tables first)
    op.drop_table("post_interests")
    op.drop_table("posts")
