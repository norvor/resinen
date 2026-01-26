import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Get DB URL from .env, default to sqlite if not found (fallback)
database_url = os.getenv("DATABASE_URL")

# Postgres connection engine
#engine = create_engine(database_url, echo=True)
engine = create_async_engine(database_url, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        # We must use run_sync() to execute synchronous metadata methods
        await conn.run_sync(Base.metadata.create_all)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session