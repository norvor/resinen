import asyncio
import httpx
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_session_factory, engine 
from app.core.security import get_password_hash
from app.models.user import User

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000/api/v1"

# --- PERSONAS ---
PERSONAS = [
    {"email": "admin@resinen.com", "pass": "admin123", "name": "Resinen Architect", "role": "superuser"},
    {"email": "alice@resinen.com", "pass": "password123", "name": "Alice Builder", "role": "user"},
    {"email": "bob@resinen.com", "pass": "password123", "name": "Bob The Critic", "role": "user"},
    {"email": "charlie@resinen.com", "pass": "password123", "name": "Charlie Newbie", "role": "user"},
    {"email": "diana@resinen.com", "pass": "password123", "name": "Diana Pro", "role": "user"},
]

async def wipe_and_bootstrap_db():
    print("\n🔥 [DB] WIPING DATABASE (Iterative Drop)...")
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = result.scalars().all()
        for table in tables:
            await conn.execute(text(f'DROP TABLE IF EXISTS "public"."{table}" CASCADE'))

        print("   -> Re-creating tables from SQLModel metadata...")
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("👤 [DB] BOOTSTRAPPING USER PERSONAS...")
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
        print(f"✅ Created {len(PERSONAS)} users in the database.")

async def login_user(client, email, password):
    try:
        res = await client.post("/auth/login", data={"username": email, "password": password})
        if res.status_code != 200:
            print(f"❌ Login failed for {email} ({res.status_code}): {res.text}")
            return None
        return {"Authorization": f"Bearer {res.json()['access_token']}"}
    except Exception as e:
        print(f"❌ Connection error logging in {email}: {str(e)}")
        return None

async def seed_via_api():
    await wipe_and_bootstrap_db()
    
    print(f"\n🚀 [API] STARTING EVOLUTION VIA: {BASE_URL}")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        
        # 1. AUTH
        print("🔑 [AUTH] Logging in...")
        tokens = {}
        for p in PERSONAS:
            auth = await login_user(client, p["email"], p["pass"])
            if auth: tokens[p["email"]] = auth
            else: return # Stop if auth fails

        admin_h = tokens.get("admin@resinen.com")
        alice_h = tokens.get("alice@resinen.com")
        bob_h = tokens.get("bob@resinen.com")
        charlie_h = tokens.get("charlie@resinen.com")
        diana_h = tokens.get("diana@resinen.com")

        # =========================================================================
        # 🌍 WORLD 1: THE NEXUS
        # =========================================================================
        print("\n🌍 [COMMUNITY] Creating 'The Nexus'...")
        nexus = await client.post("/communities/", headers=admin_h, json={
            "name": "The Nexus", "slug": "nexus", "description": "Validation World.",
            "primary_color": "#000000", "icon_url": "globe"
        })
        if nexus.status_code != 200:
            print(f"❌ Failed to create Nexus: {nexus.text}")
            return
        nexus_id = nexus.json()["id"]

        # SOCIAL
        print("   💬 [Social] Seeding posts...")
        p1 = await client.post("/social/posts", headers=admin_h, json={
            "community_id": nexus_id, "title": "Welcome", "content": "Simulation Start.", "is_pinned": True
        })
        if p1.status_code == 200:
            p1_id = p1.json()["id"]
            await client.post(f"/social/posts/{p1_id}/comments", headers=alice_h, json={"content": "Hello world!"})

        # GOVERNANCE
        print("   ⚖️ [Governance] Holding election...")
        prop = await client.post(f"/governance/{nexus_id}/proposals", headers=alice_h, json={
            "title": "Dark Mode?", "description": "Enable it?",
            "ends_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        })
        if prop.status_code == 200:
            prop_id = prop.json()["id"]
            await client.post(f"/governance/proposals/{prop_id}/vote", headers=bob_h, json={"choice": "no"})

        # =========================================================================
        # ⚔️ WORLD 3: THUNDERDOME (The Crash Fix)
        # =========================================================================
        print("\n🌍 [COMMUNITY] Creating 'Thunderdome'...")
        arena_res = await client.post("/communities/", headers=admin_h, json={
            "name": "Thunderdome", "slug": "thunder", "description": "Sports & Bets.",
            "primary_color": "#ef4444", "icon_url": "zap"
        })
        arena_id = arena_res.json()["id"]

        # --- ARENA ENGINE ---
        print("   🏆 [Arena] Configuring teams & matches...")
        
        # FIX 1: Removed 'short_code' (It doesn't exist in the DB model)
        # We handle the response safely now
        t1_res = await client.post(f"/arena/{arena_id}/teams", headers=admin_h, json={
            "name": "Red Dragons", "color": "#ff0000"
        })
        t2_res = await client.post(f"/arena/{arena_id}/teams", headers=admin_h, json={
            "name": "Blue Knights", "color": "#0000ff"
        })

        if t1_res.status_code != 200 or t2_res.status_code != 200:
            print(f"❌ Team Creation Failed: {t1_res.text} / {t2_res.text}")
            return

        t1 = t1_res.json()
        t2 = t2_res.json()
        
        # Create Match
        match_res = await client.post(f"/arena/{arena_id}/matches", headers=admin_h, json={
            "team_a_id": t1["id"],
            "team_b_id": t2["id"],
            "start_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "status": "scheduled"
        })
        
        if match_res.status_code == 200:
            match_id = match_res.json()["id"]
            
            # FIX 2: Correct Prediction Endpoint and Body
            # Endpoint: /arena/predict (Global for engine)
            # Body: {match_id, team_id} (Matches ArenaPredictionCreate)
            pred_res = await client.post(f"/arena/predict", headers=charlie_h, json={
                "match_id": match_id,
                "team_id": t1["id"]
            })
            if pred_res.status_code != 200:
                print(f"⚠️ Prediction failed: {pred_res.text}")
        else:
            print(f"❌ Match Creation Failed: {match_res.text}")

    print("\n✅ SUPER SEED COMPLETE. THE SIMULATION IS RUNNING.")

if __name__ == "__main__":
    asyncio.run(seed_via_api())