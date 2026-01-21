from typing import Generator, AsyncGenerator
from sqlmodel import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal, async_session_factory
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.models.user import User
from app.core import security
import jwt

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

# --- DATABASE DEPENDENCIES ---

# 1. Sync DB (Use this for older endpoints)
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Async DB (Use this for Social Feed & High Perf endpoints)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

# --- AUTH DEPENDENCIES ---

def get_current_user(
    db: Session = Depends(get_db),
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
    user = db.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not security.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user