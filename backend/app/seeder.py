import asyncio
import logging
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_engine, async_session_factory
from app.core.security import get_password_hash

# ----------------------------------------------------------------------
# 🏗️ IMPORT MODELS
# ----------------------------------------------------------------------
from app.models.user import User
from app.models.community import Community, Membership, Chapter
from app.models.social import Post, Comment, PostLike, CommentLike

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_db():
    """
    🧹 TABLE WIPER (Safe for Non-Superusers)
    Executes a raw SQL block that finds all tables in 'public' 
    and drops them with CASCADE.
    """
    logger.warning("💣 DROPPING ALL TABLES (CASCADE)...")
    
    async with async_engine.begin() as conn:
        # 1. Wipe Tables safely
        await conn.execute(text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """))
        
        # 2. Re-create Tables from SQLModel
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("✨ Tables Wiped & Re-created.")

async def seed_base():
    # 1. RESET
    await reset_db()

    # 2. SEED
    async with async_session_factory() as session:
        logger.info("🌱 Seeding Base Data...")

        # --- ADMIN USER ---
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
        # Flush to generate the User ID so we can use it for the Community
        await session.flush() 
        
        # --- COMMUNITY ---
        community = Community(
            name="Union Station",
            slug="union-station",
            description="The central hub for all citizens.",
            # 🚨 FIX: Plural List to match your Schema
            archetypes=["SANCTUARY"], 
            member_count=1,
            installed_engines=["social", "arena", "bazaar", "senate", "academy"],
            # 🚨 FIX: Link the Creator explicitly
            creator_id=user.id
        )
        session.add(community)
        await session.flush()

        # --- MEMBERSHIP ---
        membership = Membership(
            user_id=user.id,
            community_id=community.id,
            role="owner",
            status="active"
        )
        session.add(membership)
        
        # --- CHAPTER ---
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