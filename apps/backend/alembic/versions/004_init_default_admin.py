"""init default admin data

Revision ID: 004
Revises: 003
Create Date: 2025-12-17 10:15:00.000000

This migration can optionally initialize a default admin user.
Set INIT_DEFAULT_ADMIN=true environment variable to create the default admin on migration.
"""
import os
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Optionally initialize default admin user.

    This is a data migration that creates a default admin if:
    1. INIT_DEFAULT_ADMIN environment variable is set to 'true'
    2. The admin doesn't already exist

    To enable:
        INIT_DEFAULT_ADMIN=true alembic upgrade head

    You can also customize the admin:
        INIT_DEFAULT_ADMIN=true \
        DEFAULT_ADMIN_EMAIL=admin@example.com \
        DEFAULT_ADMIN_PASSWORD=secure123 \
        DEFAULT_ADMIN_ROLE=super_admin \
        alembic upgrade head
    """
    # Check if we should initialize default admin
    init_admin = os.getenv("INIT_DEFAULT_ADMIN", "").lower() in ["true", "1", "yes"]

    if init_admin:
        print("\n🔐 Initializing default admin user...")

        # Import here to avoid circular dependencies
        import asyncio
        import sys
        from pathlib import Path

        # Add scripts directory to path
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        sys.path.insert(0, str(scripts_dir))

        # Import and run init_admin
        try:
            # We need to run async code in sync context
            # Import the init function
            from init_admin import init_default_admin

            email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@kcardswap.local")
            password = os.getenv("DEFAULT_ADMIN_PASSWORD")
            role = os.getenv("DEFAULT_ADMIN_ROLE", "admin")

            if not password:
                print("   ⚠️  DEFAULT_ADMIN_PASSWORD not set, skipping admin creation")
                print("   Run 'python scripts/init_admin.py' manually instead")
                return

            # Run async function in sync context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context (shouldn't happen in Alembic)
                import asyncio

                asyncio.create_task(init_default_admin(email, password, role))
            else:
                # Normal Alembic sync context
                loop.run_until_complete(init_default_admin(email, password, role))

            print("   ✅ Default admin initialization complete")

        except Exception as e:
            print(f"   ⚠️  Failed to initialize admin: {e}")
            print("   You can run 'python scripts/init_admin.py' manually instead")
    else:
        # Migration runs but doesn't initialize admin
        # User can run init_admin.py script manually
        pass


def downgrade() -> None:
    """
    No downgrade action for data migration.

    This migration only adds data, not schema changes.
    If you want to remove the default admin, do it manually.
    """
    pass
