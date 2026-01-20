import asyncio
import httpx
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from sqlmodel import SQLModel, select
from app.core.database import async_session_factory, engine 
from app.core.security import get_password_hash
from app.models.user import User
# IMPORT THE ENGINE MODEL
from app.models.engine import Engine as SystemEngine 

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000/api/v1"

# --- SYSTEM ENGINES (The Missing Piece) ---
SYSTEM_ENGINES = [
    {"key": "social", "name": "Social Feed", "icon": "message-square", "description": "Posts, comments, and threads."},
    {"key": "arena", "name": "The Arena", "icon": "trophy", "description": "Competitive matches and betting."},
    {"key": "guild", "name": "Guild Hall", "icon": "users", "description": "Bounties, projects, and collaboration."},
    {"key": "listings", "name": "Bazaar", "icon": "shopping-bag", "description": "Marketplace for goods and services."},
    {"key": "bunker", "name": "The Bunker", "icon": "shield", "description": "Secret encrypted messaging."},
    {"key": "club", "name": "The Club", "icon": "glass", "description": "Events and RSVPs."},
    {"key": "garden", "name": "The Garden", "icon": "flower", "description": "Habit tracking and growth."},
    {"key": "library", "name": "Library", "icon": "book", "description": "Wiki and documentation."},
    {"key": "governance", "name": "Senate", "icon": "scale", "description": "Voting and proposals."},
    {"key": "academy", "name": "Academy", "icon": "graduation-cap", "description": "Courses and lessons."},
    {"key": "referral", "name": "Referrals", "icon": "link", "description": "Invite tracking and vouchers."},
    {"key": "stage", "name": "The Stage", "icon": "mic", "description": "Live streaming and events."}
]

# --- PERSONAS ---
PERSONAS = [
    {"email": "admin@resinen.com", "pass": "admin123", "name": "Resinen Architect", "role": "superuser"},
    {"email": "alice@resinen.com", "pass": "password123", "name": "Alice Builder", "role": "user"},
    {"email": "bob@resinen.com", "pass": "password123", "name": "Bob The Critic", "role": "user"},
    {"email": "charlie@resinen.com", "pass": "password123", "name": "Charlie Newbie", "role": "user"},
    {"email": "diana@resinen.com", "pass": "password123", "name": "Diana Pro", "role": "user"},
]

def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)

async def wipe_and_bootstrap_db():
    print("\n🔥 [DB] WIPING DATABASE (Iterative Drop)...")
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = result.scalars().all()
        for table in tables:
            await conn.execute(text(f'DROP TABLE IF EXISTS "public"."{table}" CASCADE'))

        print("   -> Re-creating tables...")
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("⚙️ [DB] SEEDING SYSTEM ENGINES...")
    async with async_session_factory() as session:
        for eng_data in SYSTEM_ENGINES:
            # Check if exists (idempotency)
            existing = await session.execute(select(SystemEngine).where(SystemEngine.key == eng_data["key"]))
            if not existing.scalars().first():
                db_eng = SystemEngine(**eng_data)
                session.add(db_eng)
        await session.commit()
        print(f"   -> {len(SYSTEM_ENGINES)} Engines online.")

    print("👤 [DB] BOOTSTRAPPING USERS...")
    async with async_session_factory() as session:
        for p in PERSONAS:
            user = User(
                email=p["email"],
                full_name=p["name"],
                hashed_password=get_password_hash(p["pass"]),
                is_superuser=(p["role"] == "superuser"),
                is_active=True,
                reputation_score=random.randint(50, 500) if p["role"] != "superuser" else 9999
            )
            session.add(user)
        await session.commit()

async def login_user(client, email, password):
    try:
        res = await client.post("/auth/login", data={"username": email, "password": password})
        if res.status_code != 200: return None
        return {"Authorization": f"Bearer {res.json()['access_token']}"}
    except: return None

async def seed_via_api():
    await wipe_and_bootstrap_db()
    
    print(f"\n🚀 [API] STARTING EVOLUTION VIA: {BASE_URL}")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        
        # 1. AUTH
        tokens = {}
        for p in PERSONAS:
            auth = await login_user(client, p["email"], p["pass"])
            if auth: tokens[p["email"]] = auth
            
        admin_h = tokens.get("admin@resinen.com")
        alice_h = tokens.get("alice@resinen.com")
        if not admin_h: 
            print("❌ Admin login failed. Server running?")
            return

        # =========================================================================
        # 🌍 WORLD 1: THE NEXUS
        # =========================================================================
        print("\n🌍 [COMMUNITY] Creating 'The Nexus'...")
        nexus = await client.post("/communities/", headers=admin_h, json={
            "name": "The Nexus", "slug": "nexus", 
            "description": "Validation World.",
            "primary_color": "#000000", "icon_url": "globe",
            "archetypes": ["social", "governance", "library", "garden"] # <--- NOW THESE EXIST!
        })
        
        if nexus.status_code == 200:
            nexus_id = nexus.json()["id"]
            
            # Seed Content
            p1 = await client.post("/social/posts", headers=admin_h, json={
                "community_id": nexus_id, "title": "System Online", "content": "Engines are active.", "is_pinned": True
            })
            
            prop = await client.post(f"/governance/{nexus_id}/proposals", headers=alice_h, json={
                "title": "Dark Mode?", "description": "Vote now.",
                "ends_at": (utc_now_naive() + timedelta(days=7)).isoformat()
            })

        # =========================================================================
        # 🛡️ WORLD 2: CODE GUILD
        # =========================================================================
        print("\n🌍 [COMMUNITY] Creating 'Code Guild'...")
        guild_res = await client.post("/communities/", headers=admin_h, json={
            "name": "Code Guild", "slug": "codex", 
            "description": "Builders only.",
            "primary_color": "#6366f1", "icon_url": "code",
            "archetypes": ["guild", "listings", "referral", "academy"]
        })

        if guild_res.status_code == 200:
            guild_id = guild_res.json()["id"]
            await client.post(f"/guild/{guild_id}/bounties", headers=admin_h, json={
                "title": "Fix Seeder", "description": "Add Engine table population.", "reward_text": "$1000"
            })

        # =========================================================================
        # ⚔️ WORLD 3: THUNDERDOME
        # =========================================================================
        print("\n🌍 [COMMUNITY] Creating 'Thunderdome'...")
        arena_res = await client.post("/communities/", headers=admin_h, json={
            "name": "Thunderdome", "slug": "thunder", 
            "description": "Enter the Arena.",
            "primary_color": "#ef4444", "icon_url": "zap",
            "archetypes": ["arena", "club", "bunker"]
        })
        
        if arena_res.status_code == 200:
            arena_id = arena_res.json()["id"]
            
            # Teams
            t1 = (await client.post(f"/arena/{arena_id}/teams", headers=admin_h, json={"name": "Red Dragons", "color": "#ff0000"})).json()
            t2 = (await client.post(f"/arena/{arena_id}/teams", headers=admin_h, json={"name": "Blue Knights", "color": "#0000ff"})).json()
            
            # Match
            await client.post(f"/arena/{arena_id}/matches", headers=admin_h, json={
                "team_a_id": t1["id"], "team_b_id": t2["id"],
                "start_time": (utc_now_naive() + timedelta(hours=1)).isoformat(),
                "status": "scheduled"
            })

    print("\n✅ SUPER SEED COMPLETE. ENGINES ARE INSTALLED.")

if __name__ == "__main__":
    asyncio.run(seed_via_api())