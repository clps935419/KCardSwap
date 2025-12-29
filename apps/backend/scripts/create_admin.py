#!/usr/bin/env python3
"""
Create Admin User Script

This script creates an admin user with email/password authentication.
Usage:
    python scripts/create_admin.py --email admin@example.com --password SecurePassword123 --role admin
    python scripts/create_admin.py --email superadmin@example.com --password SecurePassword123 --role super_admin
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.modules.identity.infrastructure.database.models.profile_model import (
    ProfileModel,
)
from app.modules.identity.infrastructure.database.models.user_model import UserModel
from app.shared.infrastructure.security.password_hasher import password_hasher


async def create_admin_user(email: str, password: str, role: str):
    """
    Create an admin user in the database.

    Args:
        email: Admin email address
        password: Admin password (will be hashed)
        role: Admin role ('admin' or 'super_admin')
    """
    # Validate role
    if role not in ["admin", "super_admin"]:
        print(f"Error: Invalid role '{role}'. Must be 'admin' or 'super_admin'.")
        sys.exit(1)

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Check if user already exists
            result = await session.execute(
                select(UserModel).where(UserModel.email == email.lower())
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"Error: User with email '{email}' already exists.")
                sys.exit(1)

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

            print("\n✅ Admin user created successfully!")
            print(f"   Email: {admin_user.email}")
            print(f"   Role: {admin_user.role}")
            print(f"   User ID: {admin_user.id}")
            print(f"   Profile created: {admin_profile.nickname}")
            print("\nYou can now login at POST /api/v1/auth/admin-login with:")
            print(
                f'   {{\n     "email": "{email}",\n     "password": "[your-password]"\n   }}'
            )

        except Exception as e:
            print(f"Error creating admin user: {e}")
            await session.rollback()
            sys.exit(1)
        finally:
            await engine.dispose()


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Create an admin user with email/password authentication"
    )
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument(
        "--password",
        required=True,
        help="Admin password (minimum 8 characters recommended)",
    )
    parser.add_argument(
        "--role",
        choices=["admin", "super_admin"],
        default="admin",
        help="Admin role (default: admin)",
    )

    args = parser.parse_args()

    # Validate password length
    if len(args.password) < 8:
        print("Warning: Password should be at least 8 characters for security.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            print("Aborted.")
            sys.exit(0)

    # Run async function
    asyncio.run(create_admin_user(args.email, args.password, args.role))


if __name__ == "__main__":
    main()
