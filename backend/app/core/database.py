from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Create Engine
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

# 2. EXPOSE THE FACTORY (This is what the Seeder needs)
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # UNCOMMENT TO RESET DB
        await conn.run_sync(SQLModel.metadata.create_all)

# 3. Use the Factory in the Dependency
async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session