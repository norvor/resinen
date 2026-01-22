import asyncio
import logging
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_engine, async_session_factory
from app.core.security import get_password_hash

# Import Models
from app.models.user import User
from app.models.engine import Engine, UserEngine
from app.models.journal import JournalEntry

logging.basicConfig(level=logging.INFO)

async def seed():
    print("🔥 NUKING DATABASE...")
    async with async_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_factory() as session:
        print("🌱 Seeding Arsenal...")
        
        # 1. Create Engines
        engines = [
            {"key": "journal", "name": "Journal", "description": "Personal Log", "icon": "book"},
            {"key": "vault", "name": "Vault", "description": "Asset Manager", "icon": "box"},
            {"key": "brain", "name": "Second Brain", "description": "Knowledge Base", "icon": "brain"},
        ]
        
        eng_map = {}
        for e in engines:
            eng = Engine(**e, is_system=True)
            session.add(eng)
            await session.flush()
            eng_map[e['key']] = eng.id
            
        # 2. Create YOU
        me = User(
            email="me@resinen.com",
            hashed_password=get_password_hash("password"),
            full_name="The Operator",
            is_superuser=True
        )
        session.add(me)
        await session.flush()
        
        # 3. Install Engines
        for key in eng_map:
            session.add(UserEngine(user_id=me.id, engine_id=eng_map[key]))
            
        await session.commit()
        print("✅ DONE. Login: me@resinen.com / password")

if __name__ == "__main__":
    asyncio.run(seed())