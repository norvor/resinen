import asyncio
import logging
from app.core.database import async_session_factory
from app.models.user import User
from app.models.community import Community, Membership
from app.core.security import get_password_hash
from sqlmodel import select

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_base():
    async with async_session_factory() as session:
        logger.info("🌱 Seeding Base Data...")

        # 1. CREATE SUPER USER
        # Check if exists to avoid duplicates
        result = await session.exec(select(User).where(User.email == "admin@unionstation.com"))
        user = result.first()
        
        if not user:
            logger.info("👤 Creating Admin User...")
            user = User(
                email="admin@unionstation.com",
                full_name="The Architect",
                username="architect",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
                avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=architect"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            logger.info("👤 Admin User already exists.")

        # 2. CREATE PRIMARY COMMUNITY
        result = await session.exec(select(Community).where(Community.slug == "union-station"))
        community = result.first()

        if not community:
            logger.info("asd Creating Union Station Community...")
            community = Community(
                name="Union Station",
                slug="union-station",
                description="The central hub for all citizens. Welcome home.",
                archetype="SANCTUARY",
                member_count=1,
                # We install all engines for the demo
                installed_engines=["social", "arena", "bazaar", "senate", "academy"]
            )
            session.add(community)
            await session.commit()
            await session.refresh(community)
        else:
            logger.info("asd Union Station Community already exists.")

        # 3. JOIN THEM (MEMBERSHIP)
        result = await session.exec(select(Membership).where(
            Membership.user_id == user.id,
            Membership.community_id == community.id
        ))
        membership = result.first()

        if not membership:
            logger.info("🔗 Linking Admin to Community...")
            membership = Membership(
                user_id=user.id,
                community_id=community.id,
                role="owner",
                status="active"
            )
            session.add(membership)
            await session.commit()
        
        logger.info("✅ BASE SEED COMPLETE")

if __name__ == "__main__":
    asyncio.run(seed_base())