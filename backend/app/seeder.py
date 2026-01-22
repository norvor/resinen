import asyncio
import logging
from sqlalchemy import text
from sqlmodel import SQLModel, select
from app.core.database import async_engine, async_session_factory
from app.core.security import get_password_hash

# 🏗️ IMPORT MODELS
from app.models.user import User
from app.models.community import Community, Membership, Chapter
from app.models.engine import Engine, CommunityEngine # <--- IMPORT THESE

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_db():
    logger.warning("💣 DROPPING ALL TABLES (CASCADE)...")
    async with async_engine.begin() as conn:
        await conn.execute(text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """))
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("✨ Tables Re-created.")

async def seed_base():
    await reset_db()

    async with async_session_factory() as session:
        logger.info("🌱 Seeding Base Data...")

        # ---------------------------------------------------------
        # 1. SEED SYSTEM ENGINES (CRITICAL STEP)
        # ---------------------------------------------------------
        logger.info("⚙️ Defining System Engines...")
        engines_data = [
            {"key": "social", "name": "Social Feed", "description": "Posts, comments, and likes", "icon": "feed"},
            {"key": "arena", "name": "The Arena", "description": "Debates and ranked discussions", "icon": "gavel"},
            {"key": "bazaar", "name": "Bazaar", "description": "Marketplace for goods and services", "icon": "store"},
            {"key": "senate", "name": "Senate", "description": "Governance and voting", "icon": "balance-scale"},
            {"key": "academy", "name": "Academy", "description": "Courses and knowledge base", "icon": "graduation-cap"},
        ]
        
        engine_map = {} # To store ID for linking later
        
        for e in engines_data:
            engine = Engine(
                key=e["key"],
                name=e["name"],
                description=e["description"],
                icon=e["icon"],
                is_system=True
            )
            session.add(engine)
            # We need to flush to get the ID immediately
            await session.flush()
            engine_map[e["key"]] = engine.id

        logger.info(f"✅ Defined {len(engine_map)} Engines.")

        # ---------------------------------------------------------
        # 2. SEED ADMIN USER
        # ---------------------------------------------------------
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
        await session.flush()
        
        # ---------------------------------------------------------
        # 3. SEED COMMUNITY (With Real Engine Links)
        # ---------------------------------------------------------
        logger.info("asd Creating Union Station Community...")
        
        # The keys we want to install
        install_keys = ["social", "arena", "bazaar", "senate", "academy"]
        
        community = Community(
            name="Union Station",
            slug="union-station",
            description="The central hub for all citizens.",
            creator_id=user.id,
            member_count=1,
            installed_engines=install_keys # JSON Column
        )
        session.add(community)
        await session.flush()

        # LINK THEM (CommunityEngine)
        for key in install_keys:
            if key in engine_map:
                link = CommunityEngine(
                    community_id=community.id,
                    engine_id=engine_map[key],
                    is_active=True,
                    config={}
                )
                session.add(link)

        # ---------------------------------------------------------
        # 4. MEMBERSHIP & CHAPTERS
        # ---------------------------------------------------------
        membership = Membership(
            user_id=user.id,
            community_id=community.id,
            role="owner",
            status="active"
        )
        session.add(membership)
        
        # FINAL COMMIT
        await session.commit()
        logger.info("✅ SEED COMPLETE")
        logger.info(f"🔑 Credentials: admin@unionstation.com / admin123")

if __name__ == "__main__":
    asyncio.run(seed_base())