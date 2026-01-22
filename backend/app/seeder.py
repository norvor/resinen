import asyncio
import logging
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.core.database import async_session_factory
from app.models.user import User
from app.models.community import Community, Membership
from app.core.security import get_password_hash

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_base():
    async with async_session_factory() as session:
        logger.info("🌱 Seeding Base Data...")

        # ---------------------------
        # 1. CREATE ADMIN USER
        # ---------------------------
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
            try:
                await session.commit()
                await session.refresh(user)
            except IntegrityError:
                await session.rollback()
                logger.warning("⚠️  User already exists (Race condition). Skipping.")
                # Re-fetch
                user = (await session.exec(select(User).where(User.email == "admin@unionstation.com"))).first()
        else:
            logger.info("⏩ Admin User already exists.")

        # ---------------------------
        # 2. CREATE COMMUNITY
        # ---------------------------
        result = await session.exec(select(Community).where(Community.slug == "union-station"))
        community = result.first()

        if not community:
            logger.info("asd Creating Union Station Community...")
            community = Community(
                name="Union Station",
                slug="union-station",
                description="The central hub for all citizens. Welcome home.",
                # FIX: Using 'archetypes' (plural list) to match your current DB structure
                archetypes=["SANCTUARY"], 
                member_count=1,
                installed_engines=["social", "arena", "bazaar", "senate", "academy"]
            )
            session.add(community)
            try:
                await session.commit()
                await session.refresh(community)
            except IntegrityError:
                await session.rollback()
                logger.warning("⚠️  Community already exists. Skipping.")
                community = (await session.exec(select(Community).where(Community.slug == "union-station"))).first()
        else:
            logger.info("⏩ Union Station Community already exists.")

        # ---------------------------
        # 3. CREATE MEMBERSHIP
        # ---------------------------
        # Ensure we have both IDs before proceeding
        if user and community:
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
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    logger.warning("⚠️  Membership already exists.")
        
        logger.info("✅ BASE SEED COMPLETE")

if __name__ == "__main__":
    asyncio.run(seed_base())