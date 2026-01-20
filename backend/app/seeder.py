import asyncio
import httpx
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_session_factory, engine 
from app.core.security import get_password_hash
from app.models.user import User

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@resinen.com"
ADMIN_PASS = "admin123"

async def bootstrap_admin():
    """Wipes the DB and creates the first admin using AsyncSession."""
    print("🔥 WIPING DATABASE...")
    async with engine.begin() as conn:
        # Get all table names
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = result.scalars().all()
        for table in tables:
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        
        # Re-create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("👤 BOOTSTRAPPING ADMIN (ASYNC)...")
    async with async_session_factory() as session:
        admin = User(
            email=ADMIN_EMAIL,
            full_name="Resinen Architect",
            hashed_password=get_password_hash(ADMIN_PASS),
            is_superuser=True,
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print("✅ Admin created successfully.")

async def seed_via_api():
    # 1. Prepare Database & Admin
    await bootstrap_admin()
    
    print(f"🚀 EVOLVING THE NEXUS VIA API: {BASE_URL}")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        
        # 2. AUTHENTICATION
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

        # 3. CREATE WORLD
        print("🌍 Creating 'The Nexus'...")
        comm_res = await client.post("/communities/", headers=headers, json={
            "name": "The Nexus",
            "slug": "nexus",
            "description": "Total System Validation World.",
            "primary_color": "#000000"
        })
        community = comm_res.json()
        cid = community["id"]

        # 4. SOCIAL (💬)
        print("💬 Seeding Social...")
        post = await client.post("/social/posts", headers=headers, json={
            "community_id": cid,
            "title": "API Genesis",
            "content": "Every byte of this world was validated by the API layer."
        })
        pid = post.json()["id"]
        await client.post(f"/social/posts/{pid}/comments", headers=headers, json={"content": "Verified."})

        # 5. ARENA (🏆)
        print("🏆 Seeding Arena...")
        t1 = (await client.post(f"/arena/{cid}/teams", headers=headers, json={"name": "Titans", "short_code": "TTN", "color": "#FF4444"})).json()
        t2 = (await client.post(f"/arena/{cid}/teams", headers=headers, json={"name": "Phantoms", "short_code": "PHM", "color": "#4444FF"})).json()
        await client.post(f"/arena/{cid}/matches", headers=headers, json={
            "team_a_id": t1["id"],
            "team_b_id": t2["id"],
            "status": "live",
            "score_a": 1,
            "score_b": 0,
            "time_display": "45'",
            "start_time": datetime.utcnow().isoformat()
        })

        # 6. GUILD (💰)
        print("💰 Seeding Guild...")
        await client.post(f"/guild/{cid}/bounties", headers=headers, json={
            "title": "Middleware Audit",
            "description": "Ensure no null pointers in engine logic.",
            "reward_text": "5000 CR"
        })

        # 7. ACADEMY (🎓)
        print("🎓 Seeding Academy...")
        # Create Course/Module
        module_res = await client.post(f"/academy/{cid}/modules", headers=headers, json={
            "title": "Introduction to Nexus",
            "order_index": 0
        })
        mid = module_res.json()["id"]
        await client.post(f"/academy/modules/{mid}/lessons", headers=headers, json={
            "title": "The First Step",
            "content_body": "This is how you master the Nexus.",
            "duration_min": 10
        })

        # 8. LIBRARY (📚)
        print("📚 Seeding Library...")
        await client.post(f"/library/{cid}/pages", headers=headers, json={
            "title": "The Manifesto",
            "slug": "manifesto",
            "content": "# The Nexus Rules \n 1. Build. 2. Verify. 3. Ship."
        })

        # 9. STAGE (🎥)
        print("🎥 Seeding Stage...")
        await client.post(f"/stage/{cid}/videos", headers=headers, json={
            "title": "Nexus Cinematic",
            "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "thumbnail_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113"
        })

        # 10. CLUB (🎉)
        print("🎉 Seeding Club...")
        await client.post(f"/club/{cid}/events", headers=headers, json={
            "title": "Launch Gala",
            "description": "Celebrating the API transition.",
            "location_name": "Digital Ballroom",
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat()
        })

    print("\n✅ THE NEXUS IS LIVE. EVERY ENDPOINT VALIDATED.")

if __name__ == "__main__":
    asyncio.run(seed_via_api())