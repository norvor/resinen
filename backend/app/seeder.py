import asyncio
import logging
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_engine, async_session_factory
from app.core.security import get_password_hash

# ----------------------------------------------------------------------
# 🏗️ IMPORT ALL MODELS HERE
# ----------------------------------------------------------------------
# If you don't import it here, the table won't be created!
from app.models.user import User
from app.models.community import Community, Membership, Chapter
from app.models.social import Post, Comment, PostLike, CommentLike, Comment
# from app.models.arena import ... 

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_db():
    """
    ☢️ NUCLEAR RESET
    Drops the entire schema to bypass Foreign Key constraints.
    """
    logger.warning("💣 DROPPING ENTIRE SCHEMA (CASCADE)...")
    
    async with async_engine.begin() as conn:
        # 1. NUKE IT
        # This kills 'user', 'reputationevent', and everything else instantly.
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        
        # 2. REBUILD IT
        # Re-grant permissions (optional but good for some setups)
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        
        # Create all tables found in imported models
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("✨ Schema & Tables Re-created Successfully.")

async def seed_base():
    # 1. EXECUTE RESET
    await reset_db()

    # 2. SEED DATA
    async with async_session_factory() as session:
        logger.info("🌱 Seeding Base Data...")

        # --- ADMIN USER ---
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
        
        # --- COMMUNITY ---
        logger.info("asd Creating Union Station Community...")
        community = Community(
            name="Union Station",
            slug="union-station",
            description="The central hub for all citizens. Welcome home.",
            # Note: Ensure this matches your model (singular 'archetype' vs plural)
            archetype="SANCTUARY", 
            member_count=1,
            installed_engines=["social", "arena", "bazaar", "senate", "academy"]
        )
        session.add(community)

        await session.commit()
        await session.refresh(user)
        await session.refresh(community)

        # --- MEMBERSHIP ---
        logger.info("🔗 Linking Admin to Community...")
        membership = Membership(
            user_id=user.id,
            community_id=community.id,
            role="owner",
            status="active"
        )
        session.add(membership)
        
        # --- CHAPTER ---
        logger.info("🛡️ Creating 'General' Chapter...")
        chapter = Chapter(
            community_id=community.id,
            name="General Hall",
            slug="general",
            description="Main discussion area",
            icon="🛡️",
            engines=["social"]
        )
        session.add(chapter)

        await session.commit()
        
        logger.info("✅ SEED COMPLETE")
        logger.info(f"🔑 Credentials: admin@unionstation.com / admin123")

if __name__ == "__main__":
    asyncio.run(seed_base())