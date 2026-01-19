import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload

from app.api import deps # Consistent dependency injection
from app.models.user import User
from app.models.guild import GuildProject, GuildBounty, BountyStatus
from app.schemas.guild import ProjectRead, ProjectCreate, BountyRead, BountyCreate

router = APIRouter()

# --- 1. LIST PROJECTS (The Showcase) ---
@router.get("/projects", response_model=List[ProjectRead])
async def list_projects(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    """Fetch the workshop floor: all projects built in this territory."""
    
    # ✅ FIX: Added joinedload for author and used proper Async execution
    stmt = (
        select(GuildProject)
        .options(joinedload(GuildProject.author))
        .where(GuildProject.community_id == community_id)
        .order_by(GuildProject.created_at.desc())
    )
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    results = []
    for p in projects:
        # Pydantic v2 model_validate or v1 from_orm
        p_read = ProjectRead.model_validate(p) if hasattr(ProjectRead, "model_validate") else ProjectRead.from_orm(p)
        
        # Inject author metadata from joined relation
        p_read.author_name = p.author.full_name if p.author else "Independent Builder"
        p_read.author_avatar = p.author.avatar_url if p.author else None
        results.append(p_read)
        
    return results

# --- 2. CREATE PROJECT (Register a Build) ---
@router.post("/projects", response_model=ProjectRead)
async def create_project(
    p_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Register a new project on the community build-log."""
    p_data = p_in.model_dump() if hasattr(p_in, "model_dump") else p_in.dict()
    
    new_proj = GuildProject(
        **p_data,
        author_id=current_user.id
    )
    db.add(new_proj)
    await db.commit()
    await db.refresh(new_proj)
    
    res = ProjectRead.model_validate(new_proj) if hasattr(ProjectRead, "model_validate") else ProjectRead.from_orm(new_proj)
    res.author_name = current_user.full_name
    res.author_avatar = current_user.avatar_url
    return res

# --- 3. LIST BOUNTIES (The Job Board) ---
@router.get("/bounties", response_model=List[BountyRead])
async def list_bounties(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    """Fetch the Wanted posters: all open bounties in this territory."""
    
    # ✅ FIX: Joinedload author to prevent async lazy-load errors in the loop
    stmt = (
        select(GuildBounty)
        .options(joinedload(GuildBounty.author))
        .where(GuildBounty.community_id == community_id)
        .where(GuildBounty.status == BountyStatus.OPEN)
        .order_by(GuildBounty.created_at.desc())
    )
    result = await db.execute(stmt)
    bounties = result.scalars().all()
    
    results = []
    for b in bounties:
        b_read = BountyRead.model_validate(b) if hasattr(BountyRead, "model_validate") else BountyRead.from_orm(b)
        
        b_read.author_name = b.author.full_name if b.author else "Anonymous Hirer"
        b_read.author_avatar = b.author.avatar_url if b.author else None
        results.append(b_read)
        
    return results

# --- 4. POST BOUNTY (The Wanted Poster) ---
@router.post("/bounties", response_model=BountyRead)
async def create_bounty(
    b_in: BountyCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Pin a new bounty to the guild's board."""
    b_data = b_in.model_dump() if hasattr(b_in, "model_dump") else b_in.dict()
    
    new_bounty = GuildBounty(
        **b_data,
        author_id=current_user.id,
        status=BountyStatus.OPEN
    )
    db.add(new_bounty)
    await db.commit()
    await db.refresh(new_bounty)
    
    res = BountyRead.model_validate(new_bounty) if hasattr(BountyRead, "model_validate") else BountyRead.from_orm(new_bounty)
    res.author_name = current_user.full_name
    res.author_avatar = current_user.avatar_url
    return res