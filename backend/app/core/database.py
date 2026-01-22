from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings
import redis

# --- URL SANITIZATION ---
# We must ensure the Sync Engine uses 'postgresql://' (psycopg2)
# and the Async Engine uses 'postgresql+asyncpg://' (asyncpg).

raw_uri = settings.DATABASE_URL

# 1. Force Sync URI (remove +asyncpg if present)
sync_uri = raw_uri.replace("+asyncpg", "")

# 2. Force Async URI (add +asyncpg if missing)
if "+asyncpg" not in raw_uri and "postgresql://" in raw_uri:
    async_uri = raw_uri.replace("postgresql://", "postgresql+asyncpg://")
else:
    async_uri = raw_uri

# --- 1. POSTGRESQL ENGINES ---

# A. Sync Engine (Standard - Uses psycopg2)
# This is safe for 'create_engine' and prevents the "MissingGreenlet" error.
engine = create_engine(
    sync_uri, 
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# B. Async Engine (Modern - Uses asyncpg)
async_engine = create_async_engine(
    async_uri,
    echo=False,
    future=True,
    pool_pre_ping=True
)

# Async Session Factory
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# --- 2. REDIS ---

class MockRedis:
    def __init__(self): self.store = {}
    def get(self, name): return self.store.get(name)
    def set(self, name, value, ex=None): self.store[name] = value; return True
    def setex(self, name, time, value): self.store[name] = value; return True
    def delete(self, *names): 
        c=0
        for n in names:
            if n in self.store: del self.store[n]; c+=1
        return c
    def ping(self): return True

try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        db=0, 
        decode_responses=True,
        socket_connect_timeout=1
    )
    redis_client.ping()
    print("✅ Redis Connected")
except Exception as e:
    print(f"⚠️  Redis Connection Failed: {e}")
    redis_client = MockRedis()

# Compatibility
async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session