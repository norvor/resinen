import asyncio
import logging
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_engine, async_session_factory
from app.core.security import get_password_hash
from app.core.config import settings

# Import Models
from app.models.user import User
from app.models.engine import Engine, UserEngine
from app.models.journal import JournalEntry 

logging.basicConfig(level=logging.INFO)

async def seed():
    print("🔥 NUKING DATABASE...")
    async with async_engine.begin() as conn:
        # 1. Drop Old Schema
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        
        # 2. Create New Schema
        await conn.execute(text("CREATE SCHEMA public"))
        
        # 3. 🛡️ RESTORE PERMISSIONS (Critical Step)
        # Grant access to the specific database user defined in your .env
        await conn.execute(text(f"GRANT ALL ON SCHEMA public TO postgres"))
        await conn.execute(text(f"GRANT ALL ON SCHEMA public TO resinen_admin"))
        await conn.execute(text(f"GRANT ALL ON SCHEMA public TO public"))
        
        # 4. Create Tables
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_factory() as session:
        print("🌱 Seeding Arsenal...")
        
        # 1. Create Engines
        engines_data = [
            {"key": "journal", "name": "Journal", "description": "Personal Log", "icon": "book"},
            {"key": "vault", "name": "Vault", "description": "Asset Manager", "icon": "box"},
            {"key": "brain", "name": "Second Brain", "description": "Knowledge Base", "icon": "brain"},
            {"key": "calendar", "name": "Calendar", "description": "Time Management", "icon": "calendar"},
        ]
        
        eng_map = {}
        for e in engines_data:
            eng = Engine(**e, is_system=True)
            session.add(eng)
            await session.flush()
            eng_map[e['key']] = eng.id
            print(f"   - Installed {e['name']}")

        # 2. Create YOU
        me = User(
            email="me@resinen.com",
            hashed_password=get_password_hash("password"),
            full_name="The Operator",
            is_superuser=True,
            avatar_url="https://api.dicebear.com/7.x/notionists/svg?seed=Operator"
        )
        session.add(me)
        await session.flush()
        print(f"   - Created User: {me.email}")
        
        # 3. Pin Engines
        for key in eng_map:
            session.add(UserEngine(
                user_id=me.id, 
                engine_id=eng_map[key],
                is_active=True,
                is_pinned=True 
            ))
            
        await session.commit()
        print("✅ DONE. Login: me@resinen.com / password")

if __name__ == "__main__":
    asyncio.run(seed())