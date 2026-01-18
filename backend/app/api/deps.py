from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import security
from app.core.config import settings
# 👇 IMPORT THE FACTORY WE MADE IN PHASE 1
from app.core.database import async_session_factory 
from app.models.user import User

# This tells FastAPI where to look for the token
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

# --- DATABASE DEPENDENCY ---
# Renamed from 'get_db' to 'get_session' to match your endpoints
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

# --- SECURITY DEPENDENCIES ---

# 1. Base: Get the user from the token
async def get_current_user(
    session: AsyncSession = Depends(get_session), # 👈 Uses the new name
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM] # 👈 Fixed to use security.ALGORITHM
        )
        token_data = payload.get("sub")
        if token_data is None:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = await session.get(User, token_data) # 👈 Uses 'session'
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 2. Level 2: Ensure user is Active
def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# 3. Level 3: Ensure user is Superuser
def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user