from typing import Generator, AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

# 1. We import the Factory from database.py
from app.core.database import SessionLocal, async_session_factory
from app.core.config import settings
from app.models.user import User
from app.core import security

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

# --- DATABASE DEPENDENCIES ---

# 1. Sync DB (Legacy/Migrations)
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Async DB (The function you are looking for!)
# This is defined HERE. It uses the factory from database.py.
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

# --- AUTH DEPENDENCIES ---

async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = security.TokenPayload(**payload)
    except (jwt.PyJWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Async Fetch
    result = await db.exec(select(User).where(User.id == token_data.sub))
    user = result.first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not security.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user