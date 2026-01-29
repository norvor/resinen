from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from dotenv import load_dotenv
import os

# --- CONNECTION STRING ---
# Ensure this matches your local setup (Postgres)
load_dotenv()  # Load environment variables from .env file
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://resinen:resinen@localhost:5432/resinen_db")

# --- ENGINE ---
# echo=True helps debug SQL queries
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# --- SESSION FACTORY (THE FIX) ---
# We use async_sessionmaker instead of the generic sessionmaker
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# --- INITIALIZATION ---
async def init_db():
    async with engine.begin() as conn:
        # Import models so SQLModel knows what to create
        from app.models import (
            User, BudgetWidget, HabitWidget, ScribbleWidget, TravelWidget, 
            TaskWidget, NoteWidget, LoveWidget, TransmissionWidget
        )
        await conn.run_sync(SQLModel.metadata.create_all)

# --- DEPENDENCY INJECTION ---
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a fresh async session for every request.
    """
    async with async_session_factory() as session:
        yield session