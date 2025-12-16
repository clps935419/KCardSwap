#!/usr/bin/env python
"""
Seed script for creating test users and profiles
Phase 3 - User Story 1
"""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.modules.identity.domain.entities.profile import Profile
from app.modules.identity.domain.entities.user import User
from app.modules.identity.infrastructure.database.models import ProfileModel, UserModel
from app.shared.infrastructure.database.connection import db_connection


async def seed_users():
    """Create test users and profiles for development and testing."""
    
    print("🌱 Starting user seed...")
    print(f"Database: {settings.DATABASE_URL}")
    
    # Test users data
    test_users = [
        {
            "google_id": "test_google_id_1",
            "email": "testuser1@example.com",
            "nickname": "CardCollector",
            "bio": "Love collecting K-pop cards!",
            "avatar_url": "https://i.pravatar.cc/300?img=1",
            "region": "Seoul",
            "privacy_flags": {
                "nearby_visible": True,
                "show_online": True,
                "allow_stranger_chat": True
            }
        },
        {
            "google_id": "test_google_id_2",
            "email": "testuser2@example.com",
            "nickname": "CardTrader",
            "bio": "Trading cards since 2020",
            "avatar_url": "https://i.pravatar.cc/300?img=2",
            "region": "Busan",
            "privacy_flags": {
                "nearby_visible": True,
                "show_online": False,
                "allow_stranger_chat": False
            }
        },
        {
            "google_id": "test_google_id_3",
            "email": "testuser3@example.com",
            "nickname": "BTS_Fan",
            "bio": "BTS Army 💜",
            "avatar_url": "https://i.pravatar.cc/300?img=3",
            "region": "Tokyo",
            "privacy_flags": {
                "nearby_visible": False,
                "show_online": True,
                "allow_stranger_chat": True
            }
        },
        {
            "google_id": "test_google_id_4",
            "email": "testuser4@example.com",
            "nickname": "BLACKPINK_Lover",
            "bio": "Collecting BLACKPINK photocards",
            "avatar_url": "https://i.pravatar.cc/300?img=4",
            "region": "Los Angeles",
            "privacy_flags": {
                "nearby_visible": True,
                "show_online": True,
                "allow_stranger_chat": True
            }
        },
        {
            "google_id": "test_google_id_5",
            "email": "testuser5@example.com",
            "nickname": "Newbie",
            "bio": None,
            "avatar_url": None,
            "region": None,
            "privacy_flags": {
                "nearby_visible": True,
                "show_online": True,
                "allow_stranger_chat": True
            }
        }
    ]
    
    # Use async session
    async with db_connection.async_session_factory() as session:
        try:
            created_count = 0
            skipped_count = 0
            
            for user_data in test_users:
                # Check if user already exists
                from sqlalchemy import select
                result = await session.execute(
                    select(UserModel).where(UserModel.google_id == user_data["google_id"])
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"⏭️  Skipping existing user: {user_data['email']}")
                    skipped_count += 1
                    continue
                
                # Create user
                user_id = uuid4()
                user_model = UserModel(
                    id=user_id,
                    google_id=user_data["google_id"],
                    email=user_data["email"]
                )
                session.add(user_model)
                
                # Create profile
                profile_model = ProfileModel(
                    user_id=user_id,
                    nickname=user_data["nickname"],
                    bio=user_data["bio"],
                    avatar_url=user_data["avatar_url"],
                    region=user_data["region"],
                    preferences={},
                    privacy_flags=user_data["privacy_flags"]
                )
                session.add(profile_model)
                
                print(f"✅ Created user: {user_data['email']} ({user_data['nickname']})")
                created_count += 1
            
            # Commit all changes
            await session.commit()
            
            print(f"\n🎉 Seed completed!")
            print(f"   Created: {created_count} users")
            print(f"   Skipped: {skipped_count} users (already exist)")
            print(f"   Total: {len(test_users)} users")
            
            # Display test user credentials
            if created_count > 0:
                print("\n📋 Test User Credentials:")
                print("=" * 60)
                for user_data in test_users:
                    print(f"Email: {user_data['email']}")
                    print(f"Google ID: {user_data['google_id']}")
                    print(f"Nickname: {user_data['nickname']}")
                    print("-" * 60)
                
                print("\n💡 To test authentication:")
                print("   1. Use Google OAuth to get a real Google ID token")
                print("   2. Or mock the GoogleOAuthService in tests")
                print("   3. For integration tests, use test fixtures with these users")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding users: {e}")
            raise


async def clear_users():
    """Clear all users and profiles (for testing)."""
    print("🗑️  Clearing all users and profiles...")
    
    async with db_connection.async_session_factory() as session:
        try:
            from sqlalchemy import delete
            
            # Delete profiles first (foreign key constraint)
            await session.execute(delete(ProfileModel))
            
            # Delete users
            await session.execute(delete(UserModel))
            
            await session.commit()
            
            print("✅ All users and profiles cleared")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error clearing users: {e}")
            raise


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed test users")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all users before seeding"
    )
    
    args = parser.parse_args()
    
    try:
        if args.clear:
            await clear_users()
        
        await seed_users()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
