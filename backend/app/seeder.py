import asyncio
import httpx
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlmodel import SQLModel, Session
from app.core.database import engine
from app.core.security import get_password_hash
from app.models.user import User # Still need the model for the very first user

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@resinen.com"
ADMIN_PASS = "admin123"

async def bootstrap_admin():
    """Wipes the DB and creates the first admin so the API has someone to talk to."""
    print("🔥 WIPING DATABASE...")
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        for table in result.scalars().all():
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("👤 BOOTSTRAPPING ADMIN...")
    with Session(engine) as session:
        admin = User(
            email=ADMIN_EMAIL,
            full_name="Resinen Architect",
            hashed_password=get_password_hash(ADMIN_PASS),
            is_superuser=True,
            is_active=True
        )
        session.add(admin)
        session.commit()

async def seed_via_api():
    await bootstrap_admin()
    
    print(f"🚀 EVOLVING THE NEXUS VIA API: {BASE_URL}")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        
        # 1. AUTHENTICATION
        print("🔑 Authenticating...")
        login_res = await client.post("/login/access-token", data={
            "username": ADMIN_EMAIL, 
            "password": ADMIN_PASS
        })
        
        if login_res.status_code != 200:
            print(f"❌ Login Failed: {login_res.text}")
            return
            
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. CREATE WORLD
        print("🌍 Creating 'The Nexus'...")
        comm_res = await client.post("/communities/", headers=headers, json={
            "name": "The Nexus",
            "slug": "nexus",
            "description": "Total System Validation World.",
            "primary_color": "#000000"
        })
        cid = comm_res.json()["id"]

        # 3. SOCIAL (💬)
        print("💬 Seeding Social...")
        post = await client.post("/social/posts", headers=headers, json={
            "community_id": cid,
            "title": "API Genesis",
            "content": "Every byte of this world was validated by the API layer."
        })
        pid = post.json()["id"]
        await client.post(f"/social/posts/{pid}/comments", headers=headers, json={"content": "Verified."})

        # 4. ARENA (🏆)
        print("🏆 Seeding Arena...")
        t1 = (await client.post(f"/arena/{cid}/teams", headers=headers, json={"name": "Titans", "short_code": "TTN", "color": "#FF0000"})).json()
        t2 = (await client.post(f"/arena/{cid}/teams", headers=headers, json={"name": "Phantoms", "short_code": "PHM", "color": "#0000FF"})).json()
        await client.post(f"/arena/{cid}/matches", headers=headers, json={
            "team_a_id": t1["id"],
            "team_b_id": t2["id"],
            "status": "live",
            "score_a": 1,
            "score_b": 0,
            "time_display": "45'",
            "start_time": datetime.utcnow().isoformat()
        })

        # 5. GUILD (💰)
        print("💰 Seeding Guild...")
        await client.post(f"/guild/{cid}/bounties", headers=headers, json={
            "title": "Middleware Audit",
            "description": "Ensure no null pointers in engine logic.",
            "reward_text": "5000 CR"
        })

        # 6. STAGE (🎥)
        print("🎥 Seeding Stage...")
        await client.post(f"/stage/{cid}/videos", headers=headers, json={
            "title": "Nexus Cinematic",
            "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "thumbnail_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113"
        })

        # 7. CLUB (🎉)
        print("🎉 Seeding Club...")
        await client.post(f"/club/{cid}/events", headers=headers, json={
            "title": "Launch Gala",
            "description": "Celebrating the API transition.",
            "location_name": "Digital Ballroom",
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat()
        })

        # 8. BAZAAR (🛍️)
        print("🛍️  Seeding Bazaar...")
        await client.post(f"/bazaar/{cid}/listings", headers=headers, json={
            "title": "Nexus Keycard",
            "description": "Access to the high-tier bunker.",
            "price_display": "100 Gold",
            "link_url": "https://resinen.com/nexus-key",
            "domain": "resinen.com"
        })

        # 9. SENATE (⚖️)
        print("⚖️  Seeding Senate...")
        await client.post(f"/governance/{cid}/proposals", headers=headers, json={
            "title": "Nexus Protocol v1",
            "description": "Adopt API-first seeding standards.",
            "ends_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        })

    print("✅ THE NEXUS IS LIVE. ALL ENDPOINTS VALIDATED.")

if __name__ == "__main__":
    asyncio.run(seed_via_api())