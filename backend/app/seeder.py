import asyncio
import httpx
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import engine
from app.core.security import get_password_hash

# We only use models here to wipe the slate clean first
async def wipe_db():
    print("🔥 WIPING DATABASE FOR FRESH START...")
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        for table in result.scalars().all():
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        await conn.run_sync(SQLModel.metadata.create_all)

async def seed_via_api():
    await wipe_db()
    
    BASE_URL = "http://localhost:8000/api/v1"
    print(f"🚀 EVOLVING THE NEXUS VIA API: {BASE_URL}")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. CREATE ADMIN (Using the direct signup or a setup endpoint)
        # Assuming you have a registration endpoint. If not, this part remains direct-DB for the very first user.
        print("👤 Authenticating Architect...")
        # (Assuming admin exists from a pre-start script or create it now)
        auth_data = {"username": "admin@resinen.com", "password": "admin123"}
        login_res = await client.post("/login/access-token", data=auth_data)
        token = login_res.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 2. CREATE THE WORLD
        print("🌍 Creating 'The Nexus'...")
        comm_res = await client.post("/communities/", headers=auth_headers, json={
            "name": "The Nexus",
            "slug": "nexus",
            "description": "API-Validated Master World.",
            "primary_color": "#000000"
        })
        cid = comm_res.json()["id"]

        # 3. SOCIAL ENGINE
        print("💬 Seeding Social Feed...")
        post_res = await client.post("/social/posts", headers=auth_headers, json={
            "community_id": cid,
            "title": "API Seeding Complete",
            "content": "This post was created via HTTP request."
        })
        pid = post_res.json()["id"]
        await client.post(f"/social/posts/{pid}/comments", headers=auth_headers, json={
            "content": "Verified via API seeder."
        })

        # 4. ARENA ENGINE
        print("🏆 Seeding Arena Teams & Matches...")
        t1 = (await client.post(f"/arena/{cid}/teams", headers=auth_headers, json={
            "name": "Alpha Squad", "short_code": "ALP", "color": "#FF0000"
        })).json()
        t2 = (await client.post(f"/arena/{cid}/teams", headers=auth_headers, json={
            "name": "Omega Group", "short_code": "OMG", "color": "#0000FF"
        })).json()
        
        await client.post(f"/arena/{cid}/matches", headers=auth_headers, json={
            "team_a_id": t1["id"],
            "team_b_id": t2["id"],
            "status": "live",
            "score_a": 2,
            "score_b": 1,
            "time_display": "65'",
            "start_time": datetime.utcnow().isoformat()
        })

        # 5. GUILD ENGINE
        print("💰 Seeding Bounties...")
        await client.post(f"/guild/{cid}/bounties", headers=auth_headers, json={
            "title": "API Refactor",
            "description": "Ensure all seeders use endpoints.",
            "reward_text": "1000 CR"
        })

        # 6. STAGE ENGINE
        print("🎥 Seeding Video...")
        await client.post(f"/stage/{cid}/videos", headers=auth_headers, json={
            "title": "The Nexus Trailer",
            "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "thumbnail_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113"
        })

        # 7. CLUB ENGINE
        print("🎉 Seeding Events...")
        await client.post(f"/club/{cid}/events", headers=auth_headers, json={
            "title": "Nexus Launch Event",
            "description": "Grand opening.",
            "location_name": "API Plaza",
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat()
        })

    print("✅ GENESIS VIA API COMPLETE. NO MODELS TOUCHED DURING POPULATION.")

if __name__ == "__main__":
    asyncio.run(seed_via_api())