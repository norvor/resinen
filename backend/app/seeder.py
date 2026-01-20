import asyncio
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.database import async_session_factory, engine 
from app.core.security import get_password_hash
from app.models.user import User

# --- CONFIG ---
ADMIN_EMAIL = "admin@resinen.com"
ADMIN_PASS = "admin123"

async def nuclear_reset():
    print("\n💥 [NUCLEAR] WIPING DATABASE...")
    
    # 1. Wipe DB (Safely handling permissions)
    async with engine.begin() as conn:
        # Get all tables in public schema
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = result.scalars().all()
        
        # Drop them one by one with CASCADE
        for table in tables:
            print(f"   -> Dropping {table}...")
            await conn.execute(text(f'DROP TABLE IF EXISTS "public"."{table}" CASCADE'))

        # Re-create schema
        print("   -> Re-creating tables...")
        await conn.run_sync(SQLModel.metadata.create_all)

    # 2. Create One Admin
    print(f"\n👤 [USER] Creating Superuser: {ADMIN_EMAIL}")
    async with async_session_factory() as session:
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=get_password_hash(ADMIN_PASS),
            full_name="System Admin",
            is_superuser=True,
            is_active=True,
            reputation_score=1000
        )
        session.add(admin)
        await session.commit()
    
    print("\n✅ DONE. Database is clean. 1 Admin exists.")

if __name__ == "__main__":
    asyncio.run(nuclear_reset())