import asyncio
from sqlmodel import SQLModel, select
from app.core.database import async_session_factory, engine # Import engine to drop tables
from app.models.user import User
from app.models.community import Community, Archetype
from app.core.security import get_password_hash

# --- CONFIGURATION ---
ADMIN_EMAIL = "admin@resinen.com"
ADMIN_PASS = "admin123"
ADMIN_NAME = "Resinen Architect"

WORLDS = [
    {
        "name": "The Colosseum",
        "slug": "colosseum",
        "archetype": Archetype.ARENA,
        "description": "The global stage for competitive glory. Live scores, prediction markets, and tribal warfare.",
        "config": {"sport": "football", "team_a": "Red", "team_b": "Blue"}
    },
    {
        "name": "Spotlight Central",
        "slug": "spotlight",
        "archetype": Archetype.STAGE,
        "description": "Visuals only. Vertical feeds, fancams, and aesthetics.",
        "config": {"view_mode": "vertical_scroll"}
    },
    {
        "name": "The Golden Temple",
        "slug": "golden-temple",
        "archetype": Archetype.SANCTUARY,
        "description": "A space for reflection, prayer, and service (Seva). Audio-first and toxicity-free.",
        "config": {"daily_hukam": True}
    },
    {
        "name": "The Great Archives",
        "slug": "archives",
        "archetype": Archetype.LIBRARY,
        "description": "Deep lore, theory crafting, and history. Beware of spoilers.",
        "config": {"spoiler_protection": True}
    },
    {
        "name": "Builders Guild",
        "slug": "builders",
        "archetype": Archetype.GUILD,
        "description": "For those who ship code. Q&A, bounties, and technical showcases.",
        "config": {"syntax_highlighting": True}
    },
    {
        "name": "Grand Bazaar",
        "slug": "bazaar",
        "archetype": Archetype.BAZAAR,
        "description": "The marketplace. Buy, sell, trade, and verify authenticity.",
        "config": {"currency": "USD", "escrow": True}
    },
    {
        "name": "The Capitol",
        "slug": "capitol",
        "archetype": Archetype.SENATE,
        "description": "Formal debate and governance. Proposals must be seconded.",
        "config": {"debate_mode": True}
    },
    {
        "name": "Training Grounds",
        "slug": "academy",
        "archetype": Archetype.ACADEMY,
        "description": "Structured learning. Complete Module 1 to unlock Module 2.",
        "config": {"curriculum_lock": True}
    },
    {
        "name": "Neon Nights",
        "slug": "neon",
        "archetype": Archetype.CLUB,
        "description": "Events, music, and the night. What happens here, stays here.",
        "config": {"ephemeral_content": True}
    },
    {
        "name": "Zero Knowledge",
        "slug": "zk-bunker",
        "archetype": Archetype.BUNKER,
        "description": "Encrypted. Anon. Burn after reading.",
        "config": {"screenshot_block": True}
    },
    {
        "name": "The Living Room",
        "slug": "lounge",
        "archetype": Archetype.LOUNGE,
        "description": "Just chilling. Find friends, plan meetups, relax.",
        "config": {"whos_online": True}
    }
]

async def seed_db():
    print("💣 WAARING: Resetting Database Protocol Initiated...")
    
    # 1. DROP OLD TABLES (The Fix)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✨ Database Wiped & Rebuilt. Clean Slate.")

    print("🌱 Starting Resinen Genesis Seeder...")
    
    async with async_session_factory() as db:
        # 2. CREATE SUPERUSER
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
        print("✅ Admin Created.")

        # 3. CREATE WORLDS
        print("Initializing 11 Sovereign Worlds...")
        for world_data in WORLDS:
            community = Community(
                name=world_data["name"],
                slug=world_data["slug"],
                description=world_data["description"],
                archetype=world_data["archetype"],
                config=world_data["config"],
                active_engines=[], # Initialize empty list
                creator_id=admin.id,
                is_private=(world_data["archetype"] == Archetype.BUNKER)
            )
            db.add(community)
        
        await db.commit()
        print("🌍 Genesis Complete. The 11 Worlds are live.")

if __name__ == "__main__":
    asyncio.run(seed_db())