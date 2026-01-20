#!/usr/bin/env python3
"""
Initialize default admin user (idempotent).

This script creates a default admin user if it doesn't already exist.
It's safe to run multiple times - it will only create the admin if missing.

This can be run:
1. Manually after migrations: python scripts/init_admin.py
2. Automatically in Docker entrypoint after alembic upgrade head
3. As part of deployment process

Environment Variables:
    DATABASE_URL              Database connection string (required)
    DEFAULT_ADMIN_EMAIL       Admin email (default: admin@kcardswap.com)
    DEFAULT_ADMIN_PASSWORD    Admin password (default: randomly generated)
    DEFAULT_ADMIN_ROLE        Admin role (default: admin)

Usage:
    # Use defaults
    python scripts/init_admin.py

    # Custom email/password via environment
    DEFAULT_ADMIN_EMAIL=admin@example.com DEFAULT_ADMIN_PASSWORD=secure123 python scripts/init_admin.py

    # Custom email/password via arguments
    python scripts/init_admin.py --email admin@example.com --password secure123 --role super_admin

    # Skip if exists (no output)
    python scripts/init_admin.py --quiet
"""

import argparse
import asyncio
import os
import secrets
import string
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.config import settings  # noqa: E402
from app.modules.identity.infrastructure.database.models.profile_model import (  # noqa: E402
    ProfileModel,
)
from app.modules.identity.infrastructure.database.models.user_model import (  # noqa: E402
    UserModel,
)
from app.shared.infrastructure.security.password_hasher import (  # noqa: E402
    password_hasher,
)


def generate_secure_password(length: int = 16) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = "".join(secrets.choice(alphabet) for i in range(length))
    return password


async def init_default_admin(email: str, password: str, role: str, quiet: bool = False):
    """
    Create default admin user if it doesn't exist (idempotent).

    Args:
        email: Admin email address
        password: Admin password (will be hashed)
        role: Admin role ('admin' or 'super_admin')
        quiet: If True, suppress output messages

    Returns:
        True if admin was created, False if it already existed
    """
    # Validate role
    if role not in ["admin", "super_admin"]:
        if not quiet:
            print(f"❌ Error: Invalid role '{role}'. Must be 'admin' or 'super_admin'.")
        return False

    # Create async engine
    database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    # Ensure asyncpg driver for async operations
    if "postgresql://" in database_url and "+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Check if admin user already exists
            result = await session.execute(
                select(UserModel).where(UserModel.email == email.lower())
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                if not quiet:
                    print(
                        f"ℹ️  Admin user '{email}' already exists (ID: {existing_user.id})"
                    )
                    print(f"   Role: {existing_user.role}")
                    print("   Skipping creation.")
                await engine.dispose()
                return False

            # Hash password
            hashed_password = password_hasher.hash(password)

            # Create admin user
            admin_user = UserModel(
                email=email.lower(),
                password_hash=hashed_password,
                role=role,
                google_id=None,  # Admin users don't use Google OAuth
            )

            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            # Create default profile for admin user
            admin_profile = ProfileModel(
                user_id=admin_user.id,
                nickname=f"Admin ({email.split('@')[0]})",
                avatar_url=None,
                bio="System Administrator",
                region=None,
                preferences={},
                privacy_flags={
                    "nearby_visible": False,
                    "show_online": False,
                    "allow_stranger_chat": False,
                },
            )
            session.add(admin_profile)
            await session.commit()

            if not quiet:
                print("\n✅ Default admin user created successfully!")
                print(f"   Email: {admin_user.email}")
                print(f"   Role: {admin_user.role}")
                print(f"   User ID: {admin_user.id}")
                print(f"   Profile created: {admin_profile.nickname}")
                print("\n   Login at: POST /api/v1/auth/admin-login")
                print(f"   Credentials: {email} / [password provided]")

            await engine.dispose()
            return True

        except Exception as e:
            if not quiet:
                print(f"❌ Error initializing admin user: {e}")
            await session.rollback()
            await engine.dispose()
            raise


async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Initialize default admin user (idempotent - safe to run multiple times)"
    )
    parser.add_argument(
        "--email",
        default=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@kcardswap.com"),
        help="Admin email address (default: admin@kcardswap.com or DEFAULT_ADMIN_EMAIL env var)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("DEFAULT_ADMIN_PASSWORD"),
        help="Admin password (default: randomly generated or DEFAULT_ADMIN_PASSWORD env var)",
    )
    parser.add_argument(
        "--role",
        choices=["admin", "super_admin"],
        default=os.getenv("DEFAULT_ADMIN_ROLE", "admin"),
        help="Admin role (default: admin or DEFAULT_ADMIN_ROLE env var)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output messages (useful in automated scripts)",
    )

    args = parser.parse_args()

    # Generate password if not provided
    if not args.password:
        password = generate_secure_password()
        if not args.quiet:
            print("⚠️  No password provided, generating random password...")
            print(f"   Generated password: {password}")
            print("   ⚠️  SAVE THIS PASSWORD - it won't be shown again!\n")
    else:
        password = args.password

    try:
        created = await init_default_admin(args.email, password, args.role, args.quiet)
        sys.exit(0 if created or args.quiet else 0)
    except Exception as e:
        if not args.quiet:
            print(f"\n❌ Failed to initialize admin: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
