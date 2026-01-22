from typing import Generator, AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt # Using PyJWT
from jwt.exceptions import InvalidTokenError

# Import Factory
from app.core.database import SessionLocal, async_session_factory
from app.core.config import settings
from app.models.user import User
from app.core import security 

# Defines the path where the frontend can get a token (for Swagger UI)
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

# --- DATABASE DEPENDENCIES ---

# 1. Sync DB (Legacy/Migrations)
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Async DB (Correct for API)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

# --- AUTH DEPENDENCIES ---

async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        # 1. Decode the token using PyJWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        
        # 2. Validate content using the Pydantic model from security.py
        token_data = security.TokenPayload(**payload)
        
    except InvalidTokenError as e:
        # This catches 'Signature has expired' or 'Invalid token'
        print(f"❌ AUTH ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # 3. Find the user in the DB
    # We await the result because we are using the Async Engine
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