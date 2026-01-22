from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.community import Community, Membership

from app.api import deps
from app.core import security
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
# We import the Read schema to ensure we send safe data to the frontend
from app.schemas.community import CommunityRead 

router = APIRouter()

@router.post("/", response_model=UserRead)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    # 1. Check existing email
    result = await db.exec(select(User).where(User.email == user_in.email))
    if result.first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Check existing username
    result = await db.exec(select(User).where(User.username == user_in.username))
    if result.first():
        raise HTTPException(status_code=400, detail="Username taken")

    # 3. Create User
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        username=user_in.username,
        is_superuser=user_in.is_superuser,
        avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_in.username}"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

@router.get("/me", response_model=UserRead)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return current_user

@router.patch("/me", response_model=UserRead)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user profile (Avatar, Bio, Name, etc).
    """
    # 1. Get clean data (ignoring nulls) using Pydantic V2 syntax
    update_data = user_in.model_dump(exclude_unset=True)
    
    # 2. Handle Password Hashing separately
    if "password" in update_data and update_data["password"]:
        hashed_password = security.get_password_hash(update_data["password"])
        current_user.hashed_password = hashed_password
        del update_data["password"]

    # 3. Update the User Object dynamically
    for key, value in update_data.items():
        setattr(current_user, key, value)
            
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/me/communities", response_model=List[CommunityRead])
async def read_my_communities(
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get list of territories (communities) the current user has joined.
    """
    # We join Membership -> Community to get the actual Community details
    # We filter for 'active' status so pending/banned communities don't show up in the main list
    query = select(Community).join(Membership).where(
        Membership.user_id == current_user.id,
        Membership.status == "active"
    )
    result = await db.execute(query)
    return result.scalars().all()