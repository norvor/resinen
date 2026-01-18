from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.community import Community, Membership

from app.api import deps
from app.core import security
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
# We import the Read schema to ensure we send safe data to the frontend
from app.schemas.community import CommunityRead 

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserRead)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    # 1. Get clean data (ignoring nulls)
    update_data = user_in.dict(exclude_unset=True)
    
    # 2. Handle Password Hashing separately
    if "password" in update_data and update_data["password"]:
        hashed_password = security.get_password_hash(update_data["password"])
        current_user.hashed_password = hashed_password
        del update_data["password"]

    # 3. Update the User Object (Cleaner logic)
    for key, value in update_data.items():
        setattr(current_user, key, value)
            
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/", response_model=UserRead)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
        
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name or "",
        is_superuser=user_in.is_superuser,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/me/communities", response_model=List[CommunityRead])
async def read_my_communities(
    db: AsyncSession = Depends(deps.get_db),
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