import asyncio
import uuid
from app.core.database import async_session_factory
from app.models.user import User
from app.models.community import Community, Membership
from app.core.security import get_password_hash

async def seed_community():
    async with async_session_factory() as session:
        print("🌱 Seeding Base Data...")

        # 1. Create User
        # Check if exists first to avoid duplicates
        user = User(
            email="citizen@unionstation.com",
            full_name="Citizen One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=citizen"
        )
        session.add(user)
        await session.flush() # Get ID without committing yet

        # 2. Create Community
        community = Community(
            name="Union Station",
            slug="union-station",
            description="The central hub for all citizens.",
            archetype="SANCTUARY",
            member_count=1,
            installed_engines=["social", "arena", "bazaar", "senate"]
        )
        session.add(community)
        await session.flush()

        # 3. Create Membership (Join them)
        membership = Membership(
            user_id=user.id,
            community_id=community.id,
            role="owner",
            status="active"
        )
        session.add(membership)

        await session.commit()
        
        print("\n✅ SEED COMPLETE")
        print("="*40)
        print(f"USER_ID:      {user.id}")
        print(f"COMMUNITY_ID: {community.id}")
        print("="*40)
        print("👉 Copy these IDs into 'seed_social.py' now.")

if __name__ == "__main__":
    asyncio.run(seed_community())