from typing import Generator, AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
import jwt

from app.core.database import SessionLocal, async_session_factory # Import the factory
from app.core.config import settings
from app.models.user import User
from app.core import security

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

# 1. Sync DB
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Async DB (Used by Auth & Social)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    # 🚨 This creates the specific AsyncSession object
    async with async_session_factory() as session:
        yield session

# 3. Current User
async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        create_access_token = security.TokenPayload(**payload)
    except Exception as e:
        # 🚨 ADD THIS PRINT STATEMENT
        print(f"❌ AUTH ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Use db.exec for SQLModel Async
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