from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID

from app.api import deps
from app.models.academic import AcademicResource
from app.models.community import Community
from app.models.user import User
from app.schemas.academic import ResourceCreate, ResourceRead

router = APIRouter()

@router.get("/", response_model=List[ResourceRead])
async def read_resources(
    community_id: UUID,  # Required: Must specify which community
    skip: int = 0,
    limit: int = 100,
    type: str = None,    # Optional: Filter by 'paper' or 'video'
    db: AsyncSession = Depends(deps.get_db),
):
    query = select(AcademicResource).where(AcademicResource.community_id == community_id)
    
    if type:
        query = query.where(AcademicResource.resource_type == type)
        
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=ResourceRead)
async def create_resource(
    *,
    db: AsyncSession = Depends(deps.get_db),
    resource_in: ResourceCreate,
    current_user: User = Depends(deps.get_current_user), # Protected
):
    # 1. Verify Community Exists
    community = await db.get(Community, resource_in.community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
        
    # 2. Create Resource
    db_resource = AcademicResource.from_orm(resource_in)
    
    # Auto-verify if Superuser (Logic can be expanded later for moderators)
    if current_user.is_superuser:
        db_resource.is_verified = True
        
    db.add(db_resource)
    await db.commit()
    await db.refresh(db_resource)
    return db_resource