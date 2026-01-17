from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.user import User
from app.models.community import Community
from app.schemas.community import CommunityCreate, CommunityRead, CommunityUpdate

router = APIRouter()

@router.get("/", response_model=List[CommunityRead])
async def read_communities(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retrieve communities.
    """
    # Just fetching all for now. You might want to filter by user later.
    query = select(Community).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=CommunityRead)
async def create_community(
    *,
    db: AsyncSession = Depends(deps.get_db),
    community_in: CommunityCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Create a new community.
    """
    # 1. Check if slug is unique
    query = select(Community).where(Community.slug == community_in.slug)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Community slug already exists")

    # 2. Create the DB Object manually (Fixing the creator_id error)
    # We unpack the frontend data (**community_in.dict())
    # AND explicitly add the creator_id from the token
    db_community = Community(
        **community_in.dict(),
        creator_id=current_user.id
    )
    
    db.add(db_community)
    await db.commit()
    await db.refresh(db_community)
    return db_community

@router.put("/{community_id}", response_model=CommunityRead)
async def update_community(
    community_id: str,
    community_in: CommunityUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a community (Only Creator)"""
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # Permission Check
    if community.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to update this community")

    # Update fields
    update_data = community_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(community, key, value)

    db.add(community)
    await db.commit()
    await db.refresh(community)
    return community

@router.delete("/{community_id}")
async def delete_community(
    community_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a community (Only Creator)"""
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    if community.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to delete this community")

    await db.delete(community)
    await db.commit()
    return {"status": "deleted"}

@router.get("/{community_id}", response_model=CommunityRead)
async def read_community(
    community_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get community by ID.
    """
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return community