from typing import Any
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token

from app.schemas.user import UserCreate, UserRead
from app.models.engine import Engine, UserEngine
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # 1. Find User by Email (Username field in form = Email)
    query = select(User).where(User.email == form_data.username)
    result = await db.exec(query)
    user = result.first()

    # 2. Verify Password
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 3. Generate Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=UserRead)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user and INITIALIZE their Arsenal.
    """
    # 1. Check if email exists
    query = select(User).where(User.email == user_in.email)
    result = await db.exec(query)
    if result.first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    # 2. Create User
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        # Generate a cool avatar based on their name
        avatar_url=f"https://api.dicebear.com/7.x/notionists/svg?seed={user_in.full_name}" 
    )
    db.add(user)
    await db.flush() # Get the ID

    # 3. 🚀 AUTO-INSTALL DEFAULT ENGINES
    # We find all "system" engines and install them for the new user
    engines_query = select(Engine).where(Engine.is_system == True)
    system_engines = await db.exec(engines_query)
    
    for engine in system_engines.all():
        install = UserEngine(
            user_id=user.id,
            engine_id=engine.id,
            is_active=True,
            is_pinned=True, # Pin them to the dock by default
            config={}
        )
        db.add(install)

    await db.commit()
    await db.refresh(user)
    
    return user