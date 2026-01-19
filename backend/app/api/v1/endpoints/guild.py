from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.user import User
from app.models.guild import GuildProject, GuildBounty, BountyStatus
from app.schemas.guild import ProjectRead, ProjectCreate, BountyRead, BountyCreate
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. LIST PROJECTS ---
@router.get("/projects", response_model=List[ProjectRead])
async def list_projects(
    community_id: str,
    db: Session = Depends(get_session)
):
    stmt = (
        select(GuildProject)
        .where(GuildProject.community_id == community_id)
        .order_by(GuildProject.created_at.desc())
    )
    projects = (await db.exec(stmt)).all()
    
    results = []
    for p in projects:
        p_read = ProjectRead.from_orm(p)
        p_read.author_name = p.author.full_name if p.author else "Builder"
        p_read.author_avatar = p.author.avatar_url if p.author else None
        results.append(p_read)
    return results

# --- 2. CREATE PROJECT ---
@router.post("/projects", response_model=ProjectRead)
async def create_project(
    p_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    new_proj = GuildProject(
        **p_in.dict(),
        author_id=current_user.id
    )
    db.add(new_proj)
    await db.commit()
    await db.refresh(new_proj)
    
    res = ProjectRead.from_orm(new_proj)
    res.author_name = current_user.full_name
    res.author_avatar = current_user.avatar_url
    return res

# --- 3. LIST BOUNTIES ---
@router.get("/bounties", response_model=List[BountyRead])
async def list_bounties(
    community_id: str,
    db: Session = Depends(get_session)
):
    stmt = (
        select(GuildBounty)
        .where(GuildBounty.community_id == community_id)
        .where(GuildBounty.status == BountyStatus.OPEN) # Only open jobs
        .order_by(GuildBounty.created_at.desc())
    )
    bounties = (await db.exec(stmt)).all()
    
    results = []
    for b in bounties:
        b_read = BountyRead.from_orm(b)
        b_read.author_name = b.author.full_name if b.author else "Hirer"
        b_read.author_avatar = b.author.avatar_url if b.author else None
        results.append(b_read)
    return results

# --- 4. POST BOUNTY ---
@router.post("/bounties", response_model=BountyRead)
async def create_bounty(
    b_in: BountyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    new_bounty = GuildBounty(
        **b_in.dict(),
        author_id=current_user.id,
        status=BountyStatus.OPEN
    )
    db.add(new_bounty)
    await db.commit()
    await db.refresh(new_bounty)
    
    res = BountyRead.from_orm(new_bounty)
    res.author_name = current_user.full_name
    res.author_avatar = current_user.avatar_url
    return res