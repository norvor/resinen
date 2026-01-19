import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_session_factory, engine 
from app.models.user import User
from app.models.community import Community, Archetype
from app.core.security import get_password_hash

# --- ENGINE MODELS ---
from app.models.listing import Listing
from app.models.governance import Proposal, ProposalStatus
from app.models.academy import Module, Lesson
from app.models.arena import ArenaTeam, ArenaMatch, MatchStatus
from app.models.club import ClubEvent
from app.models.library import LibraryPage
from app.models.stage import StageVideo
from app.models.bunker import BunkerMessage
from app.models.guild import GuildProject, GuildBounty
from app.models.garden import GardenHabit

# --- CONFIGURATION ---
ADMIN_EMAIL = "admin@resinen.com"
ADMIN_PASS = "admin123"
ADMIN_NAME = "Resinen Architect"

# --- THE 11 WORLDS ---
WORLDS = [
    {
        "name": "The Colosseum",
        "slug": "colosseum",
        "archetypes": [Archetype.ARENA],
        "description": "The global stage for competitive glory.",
        "config": {"sport": "football"}
    },
    {
        "name": "Spotlight Central",
        "slug": "spotlight",
        "archetypes": [Archetype.STAGE],
        "description": "Visuals only. Vertical feeds and aesthetics.",
        "config": {"view_mode": "vertical_scroll"}
    },
    {
        "name": "The Golden Temple",
        "slug": "golden-temple",
        "archetypes": [Archetype.SANCTUARY, Archetype.LIBRARY], # Mixed
        "description": "A space for reflection, prayer, and deep wisdom.",
        "config": {"daily_hukam": True}
    },
    {
        "name": "The Great Archives",
        "slug": "archives",
        "archetypes": [Archetype.LIBRARY],
        "description": "Deep lore, theory crafting, and history.",
        "config": {}
    },
    {
        "name": "Builders Guild",
        "slug": "builders",
        "archetypes": [Archetype.GUILD],
        "description": "For those who ship code. Q&A and bounties.",
        "config": {}
    },
    {
        "name": "Grand Bazaar",
        "slug": "bazaar",
        "archetypes": [Archetype.BAZAAR],
        "description": "The curated marketplace. Best gear only.",
        "config": {"currency": "USD"}
    },
    {
        "name": "The Capitol",
        "slug": "capitol",
        "archetypes": [Archetype.SENATE],
        "description": "Formal debate and governance.",
        "config": {"debate_mode": True}
    },
    {
        "name": "Training Grounds",
        "slug": "academy",
        "archetypes": [Archetype.ACADEMY],
        "description": "Structured learning. Level up here.",
        "config": {}
    },
    {
        "name": "Neon Nights",
        "slug": "neon",
        "archetypes": [Archetype.CLUB],
        "description": "Events, music, and the night.",
        "config": {}
    },
    {
        "name": "Zero Knowledge",
        "slug": "zk-bunker",
        "archetypes": [Archetype.BUNKER],
        "description": "Encrypted. Anon. Burn after reading.",
        "config": {}
    },
    {
        "name": "The Living Room",
        "slug": "lounge",
        "archetypes": [Archetype.LOUNGE, Archetype.GARDEN], # Mixed
        "description": "Just chilling. Habits and vibes.",
        "config": {}
    }
]

async def seed_db():
    print("🧹 STARTING SMART WIPE...")
    
    async with engine.begin() as conn:
        # Drop all tables in public schema
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"))
        tables = result.scalars().all()
        if tables:
            table_list = ", ".join([f'"{t}"' for t in tables])
            await conn.execute(text(f"DROP TABLE IF EXISTS {table_list} CASCADE;"))
            print("💥 Tables dropped.")

        # Rebuild
        await conn.run_sync(SQLModel.metadata.create_all)
        
    print("✨ Database Rebuilt.")

    async with async_session_factory() as db:
        # 1. ADMIN
        print(f"👑 Creating Superuser: {ADMIN_EMAIL}")
        admin = User(
            email=ADMIN_EMAIL,
            full_name=ADMIN_NAME,
            hashed_password=get_password_hash(ADMIN_PASS),
            is_active=True,
            is_superuser=True,
            level=99,
            reputation_score=1000,
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=admin"
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        # 2. COMMUNITIES & ENGINES
        print("🌍 Seeding Worlds & Engines...")
        
        for world_data in WORLDS:
            # Create Community
            is_private = (world_data["archetypes"][0] == Archetype.BUNKER)
            community = Community(
                name=world_data["name"],
                slug=world_data["slug"],
                description=world_data["description"],
                archetypes=world_data["archetypes"],
                config=world_data["config"],
                creator_id=admin.id,
                is_private=is_private,
                banner_url=f"https://source.unsplash.com/random/1200x400/?{world_data['slug']}"
            )
            db.add(community)
            await db.commit()
            await db.refresh(community)
            
            cid = community.id
            uid = admin.id
            primary_arch = world_data["archetypes"][0]

            # --- ENGINE SEEDING LOGIC ---
            
            # A. BAZAAR (Curated Items)
            if Archetype.BAZAAR in world_data["archetypes"]:
                items = [
                    {"title": "Sony A7IV Camera", "price": "$2498", "link": "https://amazon.com/sony-a7iv"},
                    {"title": "Mechanical Keychron Q1", "price": "$169", "link": "https://keychron.com"},
                    {"title": "Herman Miller Aeron", "price": "$1200", "link": "https://hermanmiller.com"},
                ]
                for i in items:
                    db.add(Listing(community_id=cid, curator_id=uid, title=i["title"], description="Verified best in class.", price_display=i["price"], link_url=i["link"], domain="verified-vendor.com", vouch_count=5))

            # B. SENATE (Proposals)
            if Archetype.SENATE in world_data["archetypes"]:
                props = [
                    {"title": "CIP-001: Increase Grant Funding", "desc": "Proposal to allocate 5000 USD to builders."},
                    {"title": "CIP-002: Update Code of Conduct", "desc": "Revising the toxicity guidelines."},
                ]
                for p in props:
                    db.add(Proposal(community_id=cid, author_id=uid, title=p["title"], description=p["desc"], status=ProposalStatus.ACTIVE))

            # C. ACADEMY (Modules)
            if Archetype.ACADEMY in world_data["archetypes"]:
                mod = Module(community_id=cid, title="Phase 1: Orientation", description="Learn the basics.", order_index=0)
                db.add(mod)
                await db.commit()
                await db.refresh(mod)
                db.add(Lesson(module_id=mod.id, title="Welcome to the Corps", content_body="Read this carefully...", duration_min=5, order_index=0))
                db.add(Lesson(module_id=mod.id, title="Setup Your Environment", content_body="Install VS Code...", duration_min=15, order_index=1))

            # D. ARENA (Matches)
            if Archetype.ARENA in world_data["archetypes"]:
                t1 = ArenaTeam(community_id=cid, name="Red Dragons", short_code="RED")
                t2 = ArenaTeam(community_id=cid, name="Blue Knights", short_code="BLU")
                db.add(t1); db.add(t2)
                await db.commit()
                await db.refresh(t1); await db.refresh(t2)
                
                db.add(ArenaMatch(community_id=cid, team_a_id=t1.id, team_b_id=t2.id, status=MatchStatus.LIVE, start_time=datetime.utcnow(), score_a=2, score_b=1, time_display="75'"))

            # E. CLUB (Events)
            if Archetype.CLUB in world_data["archetypes"]:
                db.add(ClubEvent(community_id=cid, creator_id=uid, title="Friday Night Mixer", description="Drinks and code.", location_name="The Lounge", start_time=datetime.utcnow() + timedelta(days=2)))

            # F. LIBRARY (Wiki)
            if Archetype.LIBRARY in world_data["archetypes"]:
                db.add(LibraryPage(community_id=cid, author_id=uid, slug="manifesto", title="The Manifesto", content="We build for the future."))
                db.add(LibraryPage(community_id=cid, author_id=uid, slug="rules", title="Community Rules", content="1. Be kind. 2. Ship code."))

            # G. STAGE (Videos)
            if Archetype.STAGE in world_data["archetypes"]:
                db.add(StageVideo(community_id=cid, author_id=uid, title="Morning Routine", video_url="https://example.com/vid1.mp4", thumbnail_url="https://source.unsplash.com/random/300x500", duration_sec=15))

            # H. BUNKER (Messages)
            if Archetype.BUNKER in world_data["archetypes"]:
                db.add(BunkerMessage(community_id=cid, author_id=uid, content="The passcode is 4492. Burn this.", is_anonymous=True, expires_at=datetime.utcnow() + timedelta(minutes=30)))

            # I. GUILD (Projects)
            if Archetype.GUILD in world_data["archetypes"]:
                db.add(GuildProject(community_id=cid, author_id=uid, title="Resinen Engine", description="A decentralized city OS.", tech_stack="Python, Svelte"))
                db.add(GuildBounty(community_id=cid, author_id=uid, title="Fix Login Bug", description="Auth token expiring too fast.", reward_text="$500 Bounty"))

            # J. GARDEN (Habits)
            if Archetype.GARDEN in world_data["archetypes"] or Archetype.LOUNGE in world_data["archetypes"]:
                db.add(GardenHabit(community_id=cid, user_id=uid, title="Morning Meditation", icon="🧘", streak_current=5, streak_best=12))

        await db.commit()
        print("🚀 Genesis Complete. All systems operational.")

if __name__ == "__main__":
    asyncio.run(seed_db())