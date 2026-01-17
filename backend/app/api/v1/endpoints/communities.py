from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.community import Community
from app.schemas.community import CommunityCreate, CommunityRead

router = APIRouter()

@router.post("/", response_model=CommunityRead)
async def create_community(
    *,
    db: AsyncSession = Depends(deps.get_db),
    community_in: CommunityCreate
):
    # Check for slug collision
    result = await db.execute(select(Community).where(Community.slug == community_in.slug))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Slug already exists")

    db_community = Community.from_orm(community_in)
    db.add(db_community)
    await db.commit()
    await db.refresh(db_community)
    return db_community

@router.get("/", response_model=List[CommunityRead])
async def read_communities(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
):
    result = await db.execute(select(Community).offset(skip).limit(limit))
    return result.scalars().all()