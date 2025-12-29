"""add Phase 6 tables for friends, chat, ratings, and reports

Revision ID: 008
Revises: 007
Create Date: 2025-12-21 09:30:00.000000

Add tables for Phase 6 User Story 4: Friend System and Chat
- friendships: friend relationships and blocking
- chat_rooms: one-on-one chat rooms
- messages: chat messages with polling support
- ratings: user ratings after trades
- reports: user reports for violations
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Phase 6 tables (idempotent)."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    # 1. Create friendships table
    if "friendships" not in tables:
        op.create_table(
            "friendships",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("uuid_generate_v4()"),
            ),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("friend_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column(
                "status", sa.String(length=50), nullable=False, server_default="pending"
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            # Foreign key constraints
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["friend_id"], ["users.id"], ondelete="CASCADE"),
        )

        # Create trigger for automatic updated_at
        op.execute(
            """
            CREATE TRIGGER update_friendships_updated_at
            BEFORE UPDATE ON friendships
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        )

    # Create indexes for friendships
    indexes = (
        [idx["name"] for idx in inspector.get_indexes("friendships")]
        if "friendships" in tables
        else []
    )

    if "idx_friendships_user_id" not in indexes:
        op.create_index("idx_friendships_user_id", "friendships", ["user_id"])

    if "idx_friendships_friend_id" not in indexes:
        op.create_index("idx_friendships_friend_id", "friendships", ["friend_id"])

    if "idx_friendship_users" not in indexes:
        op.create_index("idx_friendship_users", "friendships", ["user_id", "friend_id"])

    if "idx_friendship_status" not in indexes:
        op.create_index("idx_friendship_status", "friendships", ["status"])

    # 2. Create chat_rooms table
    if "chat_rooms" not in tables:
        op.create_table(
            "chat_rooms",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("uuid_generate_v4()"),
            ),
            sa.Column(
                "participant_ids",
                postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    # Create index for chat_rooms
    indexes = (
        [idx["name"] for idx in inspector.get_indexes("chat_rooms")]
        if "chat_rooms" in tables
        else []
    )

    if "idx_chat_room_participants" not in indexes:
        op.create_index("idx_chat_room_participants", "chat_rooms", ["participant_ids"])

    # 3. Create messages table
    if "messages" not in tables:
        op.create_table(
            "messages",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("uuid_generate_v4()"),
            ),
            sa.Column("room_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column(
                "status", sa.String(length=50), nullable=False, server_default="sent"
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                index=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            # Foreign key constraints
            sa.ForeignKeyConstraint(["room_id"], ["chat_rooms.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        )

        # Create trigger for automatic updated_at
        op.execute(
            """
            CREATE TRIGGER update_messages_updated_at
            BEFORE UPDATE ON messages
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        )

    # Create indexes for messages (critical for polling performance)
    indexes = (
        [idx["name"] for idx in inspector.get_indexes("messages")]
        if "messages" in tables
        else []
    )

    if "idx_messages_room_id" not in indexes:
        op.create_index("idx_messages_room_id", "messages", ["room_id"])

    if "idx_messages_sender_id" not in indexes:
        op.create_index("idx_messages_sender_id", "messages", ["sender_id"])

    if "idx_message_room_created" not in indexes:
        op.create_index(
            "idx_message_room_created", "messages", ["room_id", "created_at"]
        )

    if "idx_message_room_id" not in indexes:
        op.create_index("idx_message_room_id", "messages", ["room_id", "id"])

    if "idx_message_status_sender" not in indexes:
        op.create_index(
            "idx_message_status_sender", "messages", ["room_id", "status", "sender_id"]
        )

    if "idx_messages_status" not in indexes:
        op.create_index("idx_messages_status", "messages", ["status"])

    # 4. Create ratings table
    if "ratings" not in tables:
        op.create_table(
            "ratings",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("uuid_generate_v4()"),
            ),
            sa.Column("rater_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("rated_user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("trade_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("score", sa.Integer(), nullable=False),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                index=True,
            ),
            # Foreign key constraints
            sa.ForeignKeyConstraint(["rater_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["rated_user_id"], ["users.id"], ondelete="CASCADE"
            ),
            # Note: trade_id FK will be added when Trade module is implemented
        )

    # Create indexes for ratings
    indexes = (
        [idx["name"] for idx in inspector.get_indexes("ratings")]
        if "ratings" in tables
        else []
    )

    if "idx_ratings_rater_id" not in indexes:
        op.create_index("idx_ratings_rater_id", "ratings", ["rater_id"])

    if "idx_ratings_rated_user_id" not in indexes:
        op.create_index("idx_ratings_rated_user_id", "ratings", ["rated_user_id"])

    if "idx_ratings_trade_id" not in indexes:
        op.create_index("idx_ratings_trade_id", "ratings", ["trade_id"])

    if "idx_rating_trade_rater" not in indexes:
        op.create_index(
            "idx_rating_trade_rater", "ratings", ["trade_id", "rater_id"], unique=True
        )

    if "idx_rating_rated_user" not in indexes:
        op.create_index("idx_rating_rated_user", "ratings", ["rated_user_id", "score"])

    # 5. Create reports table
    if "reports" not in tables:
        op.create_table(
            "reports",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("uuid_generate_v4()"),
            ),
            sa.Column("reporter_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column(
                "reported_user_id", postgresql.UUID(as_uuid=True), nullable=False
            ),
            sa.Column("reason", sa.String(length=100), nullable=False),
            sa.Column("detail", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                index=True,
            ),
            sa.Column("resolved", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
            # Foreign key constraints
            sa.ForeignKeyConstraint(["reporter_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["reported_user_id"], ["users.id"], ondelete="CASCADE"
            ),
        )

    # Create indexes for reports
    indexes = (
        [idx["name"] for idx in inspector.get_indexes("reports")]
        if "reports" in tables
        else []
    )

    if "idx_reports_reporter_id" not in indexes:
        op.create_index("idx_reports_reporter_id", "reports", ["reporter_id"])

    if "idx_reports_reported_user_id" not in indexes:
        op.create_index("idx_reports_reported_user_id", "reports", ["reported_user_id"])

    if "idx_reports_reason" not in indexes:
        op.create_index("idx_reports_reason", "reports", ["reason"])

    if "idx_reports_resolved" not in indexes:
        op.create_index("idx_reports_resolved", "reports", ["resolved"])

    if "idx_report_resolved_created" not in indexes:
        op.create_index(
            "idx_report_resolved_created", "reports", ["resolved", "created_at"]
        )

    if "idx_report_user_reason" not in indexes:
        op.create_index(
            "idx_report_user_reason", "reports", ["reported_user_id", "reason"]
        )


def downgrade() -> None:
    """Drop Phase 6 tables (idempotent)."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    # Drop in reverse order due to foreign key constraints

    # 5. Drop reports table
    if "reports" in tables:
        indexes = [idx["name"] for idx in inspector.get_indexes("reports")]
        for idx_name in [
            "idx_report_user_reason",
            "idx_report_resolved_created",
            "idx_reports_resolved",
            "idx_reports_reason",
            "idx_reports_reported_user_id",
            "idx_reports_reporter_id",
        ]:
            if idx_name in indexes:
                op.drop_index(idx_name, "reports")
        op.drop_table("reports")

    # 4. Drop ratings table
    if "ratings" in tables:
        indexes = [idx["name"] for idx in inspector.get_indexes("ratings")]
        for idx_name in [
            "idx_rating_rated_user",
            "idx_rating_trade_rater",
            "idx_ratings_trade_id",
            "idx_ratings_rated_user_id",
            "idx_ratings_rater_id",
        ]:
            if idx_name in indexes:
                op.drop_index(idx_name, "ratings")
        op.drop_table("ratings")

    # 3. Drop messages table
    if "messages" in tables:
        op.execute("DROP TRIGGER IF EXISTS update_messages_updated_at ON messages;")
        indexes = [idx["name"] for idx in inspector.get_indexes("messages")]
        for idx_name in [
            "idx_messages_status",
            "idx_message_status_sender",
            "idx_message_room_id",
            "idx_message_room_created",
            "idx_messages_sender_id",
            "idx_messages_room_id",
        ]:
            if idx_name in indexes:
                op.drop_index(idx_name, "messages")
        op.drop_table("messages")

    # 2. Drop chat_rooms table
    if "chat_rooms" in tables:
        indexes = [idx["name"] for idx in inspector.get_indexes("chat_rooms")]
        if "idx_chat_room_participants" in indexes:
            op.drop_index("idx_chat_room_participants", "chat_rooms")
        op.drop_table("chat_rooms")

    # 1. Drop friendships table
    if "friendships" in tables:
        op.execute(
            "DROP TRIGGER IF EXISTS update_friendships_updated_at ON friendships;"
        )
        indexes = [idx["name"] for idx in inspector.get_indexes("friendships")]
        for idx_name in [
            "idx_friendship_status",
            "idx_friendship_users",
            "idx_friendships_friend_id",
            "idx_friendships_user_id",
        ]:
            if idx_name in indexes:
                op.drop_index(idx_name, "friendships")
        op.drop_table("friendships")
