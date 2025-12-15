#!/usr/bin/env python3
"""
Database seed script for development and testing environments.

This script populates the database with sample data for testing and development.

Usage:
    poetry run python scripts/seed.py [--clear]

Options:
    --clear     Clear existing data before seeding (WARNING: Destructive!)

Environment Variables:
    DATABASE_URL    Database connection string (required)
"""
import asyncio
import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import List
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.infrastructure.database.models import (
    UserModel,
    ProfileModel,
    RefreshTokenModel,
    Base
)


class DatabaseSeeder:
    """Seeds the database with sample data."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def clear_data(self):
        """Clear all existing data from tables."""
        print("⚠️  Clearing existing data...")
        
        # Delete in order to respect foreign keys
        await self.session.execute(text("DELETE FROM refresh_tokens"))
        await self.session.execute(text("DELETE FROM cards"))
        await self.session.execute(text("DELETE FROM subscriptions"))
        await self.session.execute(text("DELETE FROM profiles"))
        await self.session.execute(text("DELETE FROM users"))
        
        await self.session.commit()
        print("✓ Data cleared")
    
    async def seed_users(self) -> List[UserModel]:
        """Create sample users."""
        print("Creating sample users...")
        
        users_data = [
            {
                "google_id": "google_user_1",
                "email": "alice@example.com",
                "nickname": "Alice",
                "bio": "K-pop enthusiast and card collector!",
                "region": "Taiwan",
            },
            {
                "google_id": "google_user_2",
                "email": "bob@example.com",
                "nickname": "Bob",
                "bio": "Casual collector, love trading!",
                "region": "Japan",
            },
            {
                "google_id": "google_user_3",
                "email": "charlie@example.com",
                "nickname": "Charlie",
                "bio": "BTS fan forever 💜",
                "region": "Korea",
            },
            {
                "google_id": "google_user_4",
                "email": "diana@example.com",
                "nickname": "Diana",
                "bio": "Collecting since 2015",
                "region": "USA",
            },
            {
                "google_id": "google_user_5",
                "email": "eve@example.com",
                "nickname": "Eve",
                "bio": "Looking for rare cards!",
                "region": "Singapore",
            },
        ]
        
        users = []
        for user_data in users_data:
            # Create user
            user = UserModel(
                google_id=user_data["google_id"],
                email=user_data["email"]
            )
            self.session.add(user)
            await self.session.flush()
            
            # Create profile
            profile = ProfileModel(
                user_id=user.id,
                nickname=user_data["nickname"],
                bio=user_data.get("bio"),
                region=user_data.get("region"),
                preferences={"language": "en", "theme": "light"},
                privacy_flags={
                    "nearby_visible": True,
                    "show_online": True,
                    "allow_stranger_chat": True
                }
            )
            self.session.add(profile)
            
            users.append(user)
        
        await self.session.commit()
        print(f"✓ Created {len(users)} users with profiles")
        return users
    
    async def seed_refresh_tokens(self, users: List[UserModel]):
        """Create sample refresh tokens."""
        print("Creating sample refresh tokens...")
        
        tokens = []
        for user in users[:3]:  # Only first 3 users have active tokens
            token = RefreshTokenModel(
                user_id=user.id,
                token=f"refresh_token_{uuid.uuid4()}",
                expires_at=datetime.utcnow() + timedelta(days=7),
                revoked=False
            )
            self.session.add(token)
            tokens.append(token)
        
        await self.session.commit()
        print(f"✓ Created {len(tokens)} refresh tokens")
    
    async def seed_all(self, clear: bool = False):
        """Seed all sample data."""
        if clear:
            await self.clear_data()
        
        print("\n🌱 Seeding database...")
        print("=" * 50)
        
        users = await self.seed_users()
        await self.seed_refresh_tokens(users)
        
        print("=" * 50)
        print("✅ Database seeding completed!\n")
        print(f"Sample users created: {len(users)}")
        print("\nYou can now:")
        print("  - Login as: alice@example.com, bob@example.com, etc.")
        print("  - Test API endpoints with seeded data")
        print("  - View data in database")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Seed the database with sample data")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding (WARNING: Destructive!)"
    )
    args = parser.parse_args()
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nExample:")
        print('  export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db"')
        print("  poetry run python scripts/seed.py")
        sys.exit(1)
    
    # Ensure asyncpg driver
    if "postgresql://" in database_url and "+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Confirm if clearing data
    if args.clear:
        print("\n⚠️  WARNING: This will delete all existing data!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
    
    # Create engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            seeder = DatabaseSeeder(session)
            await seeder.seed_all(clear=args.clear)
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
