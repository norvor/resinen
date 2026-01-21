from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings
import redis

# --- 1. POSTGRESQL (Sync & Async) ---

# Sync Engine (Used by some legacy dependencies or migrations)
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Engine (Used by FastAPI endpoints)
# Ensure your config.py has SQLALCHEMY_DATABASE_URI starting with 'postgresql+asyncpg://'
# If not, you might need to construct it:
# ASYNC_URI = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    future=True,
    pool_pre_ping=True
)

# --- 2. REDIS (Caching Layer) ---

class MockRedis:
    """Fallback in-memory cache if Redis is offline."""
    def __init__(self): 
        self.store = {}
        print("⚠️  Running with MockRedis (In-Memory). Data will vanish on restart.")

    def get(self, name): 
        return self.store.get(name)

    def set(self, name, value, ex=None): 
        self.store[name] = value
        return True

    def setex(self, name, time, value): 
        self.store[name] = value
        return True

    def delete(self, *names): 
        count = 0
        for name in names: 
            if name in self.store: 
                del self.store[name]
                count += 1
        return count
    
    def ping(self):
        return True

try:
    # Try connecting to Redis container
    redis_client = redis.Redis(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        db=0, 
        decode_responses=True, # Auto-decode bytes to strings
        socket_connect_timeout=1 # Fail fast if not found
    )
    redis_client.ping() # Trigger connection check
    print("✅ Redis Connected")
except Exception as e:
    print(f"⚠️  Redis Connection Failed: {e}")
    redis_client = MockRedis()