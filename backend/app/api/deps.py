from typing import Generator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session

# This allows any route to ask for "db: AsyncSession"
async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session