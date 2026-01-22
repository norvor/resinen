import asyncio
import logging
from sqlmodel import SQLModel, select
from app.core.database import async_engine, async_session_factory
from app.core.security import get_password_hash

# ----------------------------------------------------------------------
# 🏗️ IMPORT ALL MODELS HERE
# ----------------------------------------------------------------------
# This is crucial! SQLModel needs to know about these classes 
# before it can create the tables in the database.
from app.models.user import User
from app.models.community import Community, Membership, Chapter
from app.models.social import Post, Comment, PostLike, CommentLike
# from app.models.arena import ... (Add future engines here)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_db():
    """
    ⚠️ WARNING: DELETES ALL DATA
    Drops all tables and recreates them from SQLModel metadata.
    """
    logger.warning("💣 DROPPING ALL TABLES & RESETTING SCHEMA...")
    
    async with async_engine.begin() as conn:
        # Disable foreign key checks temporarily to avoid dependency errors during drop
        # (Postgres specific, but good practice)
        # await conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")) 
        
        # Standard SQLModel Drop/Create
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("✨ Database Schema Re-created Successfully.")

async def seed_base():
    # 1. WIPE THE DATABASE
    await reset_db()

    # 2. SEED DATA
    async with async_session_factory() as session:
        logger.info("🌱 Seeding Base Data...")

        # --- CREATE ADMIN USER ---
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
        
        # --- CREATE COMMUNITY ---
        logger.info("asd Creating Union Station Community...")
        community = Community(
            name="Union Station",
            slug="union-station",
            description="The central hub for all citizens. Welcome home.",
            archetype="SANCTUARY", # Correct singular field based on your schema
            member_count=1,
            installed_engines=["social", "arena", "bazaar", "senate", "academy"]
        )
        session.add(community)

        # Commit here so we get IDs for the Membership
        await session.commit()
        await session.refresh(user)
        await session.refresh(community)

        # --- CREATE MEMBERSHIP ---
        logger.info("🔗 Linking Admin to Community...")
        membership = Membership(
            user_id=user.id,
            community_id=community.id,
            role="owner",
            status="active"
        )
        session.add(membership)
        
        # --- CREATE DEFAULT CHAPTER (Optional) ---
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
        
        logger.info("✅ NUCLEAR SEED COMPLETE")
        logger.info(f"🔑 User: admin@unionstation.com / admin123")
        logger.info(f"🌍 Community: {community.id}")

if __name__ == "__main__":
    asyncio.run(seed_base())