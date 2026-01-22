import asyncio
import logging
from sqlmodel import SQLModel
from app.core.database import async_engine, async_session_factory
from app.core.security import get_password_hash

# Import Models (Critical for drop_all/create_all to know what to target)
from app.models.user import User
from app.models.engine import Engine, UserEngine
from app.models.journal import JournalEntry 
# from app.models.vault import VaultItem 
# from app.models.library import Page

logging.basicConfig(level=logging.INFO)

async def seed():
    print("🔥 CLEANING DATABASE (Dropping Tables)...")
    
    async with async_engine.begin() as conn:
        # 1. 🚨 SAFE FIX: Drop tables only, not the schema
        # This respects permissions and works perfectly
        await conn.run_sync(SQLModel.metadata.drop_all)
        
        # 2. Re-create Tables
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