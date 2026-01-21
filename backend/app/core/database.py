from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings
import redis
from typing import AsyncGenerator

# --- 1. POSTGRESQL (Sync & Async) ---

# Sync Engine (Legacy/Migrations)
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Engine (FastAPI Endpoints)
# Ensure URI is async compatible
async_uri = settings.DATABASE_URL
if async_uri.startswith("postgresql://"):
    async_uri = async_uri.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    async_uri,
    echo=False,
    future=True,
    pool_pre_ping=True
)

# 🚨 THE MISSING PART: Export the Factory 🚨
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# --- 2. REDIS (Caching Layer) ---

class MockRedis:
    def __init__(self): 
        self.store = {}
        print("⚠️  Running with MockRedis (In-Memory). Data will vanish on restart.")
    def get(self, name): return self.store.get(name)
    def set(self, name, value, ex=None): 
        self.store[name] = value
        return True
    def setex(self, name, time, value): 
        self.store[name] = value
        return True
    def delete(self, *names): 
        for name in names: 
            if name in self.store: del self.store[name]
        return len(names)
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
    
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session