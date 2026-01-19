import asyncio
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_session_factory, engine 
from app.models.user import User
from app.models.community import Community, Archetype
from app.core.security import get_password_hash

# --- CONFIGURATION ---
ADMIN_EMAIL = "admin@resinen.com"
ADMIN_PASS = "admin123"
ADMIN_NAME = "Resinen Architect"

# 🚨 UPDATED: Now using 'archetypes' (List) instead of single value
WORLDS = [
    {
        "name": "The Colosseum",
        "slug": "colosseum",
        "archetypes": [Archetype.ARENA], # <--- List
        "description": "The global stage for competitive glory. Live scores, prediction markets, and tribal warfare.",
        "config": {"sport": "football", "team_a": "Red", "team_b": "Blue"}
    },
    {
        "name": "Spotlight Central",
        "slug": "spotlight",
        "archetypes": [Archetype.STAGE],
        "description": "Visuals only. Vertical feeds, fancams, and aesthetics.",
        "config": {"view_mode": "vertical_scroll"}
    },
    {
        "name": "The Golden Temple",
        "slug": "golden-temple",
        "archetypes": [Archetype.SANCTUARY],
        "description": "A space for reflection, prayer, and service (Seva). Audio-first and toxicity-free.",
        "config": {"daily_hukam": True}
    },
    {
        "name": "The Great Archives",
        "slug": "archives",
        "archetypes": [Archetype.LIBRARY],
        "description": "Deep lore, theory crafting, and history. Beware of spoilers.",
        "config": {"spoiler_protection": True}
    },
    {
        "name": "Builders Guild",
        "slug": "builders",
        "archetypes": [Archetype.GUILD],
        "description": "For those who ship code. Q&A, bounties, and technical showcases.",
        "config": {"syntax_highlighting": True}
    },
    {
        "name": "Grand Bazaar",
        "slug": "bazaar",
        "archetypes": [Archetype.BAZAAR],
        "description": "The marketplace. Buy, sell, trade, and verify authenticity.",
        "config": {"currency": "USD", "escrow": True}
    },
    {
        "name": "The Capitol",
        "slug": "capitol",
        "archetypes": [Archetype.SENATE],
        "description": "Formal debate and governance. Proposals must be seconded.",
        "config": {"debate_mode": True}
    },
    {
        "name": "Training Grounds",
        "slug": "academy",
        "archetypes": [Archetype.ACADEMY],
        "description": "Structured learning. Complete Module 1 to unlock Module 2.",
        "config": {"curriculum_lock": True}
    },
    {
        "name": "Neon Nights",
        "slug": "neon",
        "archetypes": [Archetype.CLUB],
        "description": "Events, music, and the night. What happens here, stays here.",
        "config": {"ephemeral_content": True}
    },
    {
        "name": "Zero Knowledge",
        "slug": "zk-bunker",
        "archetypes": [Archetype.BUNKER],
        "description": "Encrypted. Anon. Burn after reading.",
        "config": {"screenshot_block": True}
    },
    {
        "name": "The Living Room",
        "slug": "lounge",
        "archetypes": [Archetype.LOUNGE],
        "description": "Just chilling. Find friends, plan meetups, relax.",
        "config": {"whos_online": True}
    }
]

async def seed_db():
    print("🧹 STARTING SMART WIPE (Permission Friendly)...")
    
    async with engine.begin() as conn:
        # 1. FIND ALL TABLES
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"))
        tables = result.scalars().all()
        
        if tables:
            print(f"Found {len(tables)} tables to destroy: {tables}")
            # 2. DROP THEM WITH CASCADE
            table_list = ", ".join([f'"{t}"' for t in tables])
            await conn.execute(text(f"DROP TABLE IF EXISTS {table_list} CASCADE;"))
            print("💥 All tables dropped successfully.")
        else:
            print("Table empty. Nothing to drop.")

        # 3. REBUILD
        await conn.run_sync(SQLModel.metadata.create_all)
        
    print("✨ Database Rebuilt from Scratch.")

    async with async_session_factory() as db:
        # 4. CREATE SUPERUSER
        print(f"Creating Superuser: {ADMIN_EMAIL}")
        admin = User(
            email=ADMIN_EMAIL,
            full_name=ADMIN_NAME,
            hashed_password=get_password_hash(ADMIN_PASS),
            is_active=True,
            is_superuser=True,
            level=99,
            reputation_score=1000
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        # 5. CREATE WORLDS
        print("Initializing 11 Sovereign Worlds...")
        for world_data in WORLDS:
            # 🚨 CHECK: Ensure is_private logic uses the first archetype in the list
            is_private = (world_data["archetypes"][0] == Archetype.BUNKER)

            community = Community(
                name=world_data["name"],
                slug=world_data["slug"],
                description=world_data["description"],
                
                # 🚨 UPDATED FIELD
                archetypes=world_data["archetypes"], 
                
                config=world_data["config"],
                installed_engines=[], # Renamed from active_engines in recent schemas? Check your model.
                creator_id=admin.id,
                is_private=is_private
            )
            db.add(community)
        
        await db.commit()
        print("🌍 Genesis Complete. The 11 Worlds are live.")

if __name__ == "__main__":
    asyncio.run(seed_db())