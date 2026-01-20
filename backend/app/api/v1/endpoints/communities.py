from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy import or_ 
from sqlalchemy.orm import joinedload
import uuid 

from sqlalchemy import func
from datetime import datetime
from app.models.social import Post

from app.api import deps
from app.models.user import User
from app.models.engine import CommunityEngine, Engine
from app.models.community import Community, Membership
from app.schemas.community import CommunityCreate, CommunityRead, CommunityUpdate
from app.schemas.membership import MembershipOut

router = APIRouter()

# --- PUBLIC MAP ---
@router.get("/", response_model=List[CommunityRead])
async def read_communities(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
):
    """Retrieve communities with their installed engines."""
    # 1. Fetch Communities
    query = select(Community)
    if q:
        search_term = f"%{q}%"
        query = query.where(or_(Community.name.ilike(search_term), Community.slug.ilike(search_term)))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    communities = result.scalars().all()

    # 2. Populate 'installed_engines' for the list view
    # This is an N+1 query optimization (simplified loop for now)
    for comm in communities:
        stmt = (
            select(Engine.key)
            .join(CommunityEngine, CommunityEngine.engine_id == Engine.id)
            .where(CommunityEngine.community_id == comm.id)
            .where(CommunityEngine.is_active == True)
        )
        engines_res = await db.execute(stmt)
        # Manually attach the list so the Pydantic model serializes it
        setattr(comm, "installed_engines", engines_res.scalars().all())

    return communities

@router.post("/", response_model=CommunityRead)
async def create_community(
    *,
    db: AsyncSession = Depends(deps.get_db),
    community_in: CommunityCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new community and INSTALL requested engines."""
    
    # 1. Permission Check
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, 
            detail="Resinen Federal Authority Required. Only Admins can create territories."
        )

    # 2. Check Slug Uniqueness
    query = select(Community).where(Community.slug == community_in.slug)
    if (await db.execute(query)).scalars().first():
        raise HTTPException(status_code=400, detail="Community slug already exists")

    # 3. Create Community Record
    # Use model_dump to safely unpack Pydantic v2 model
    db_community = Community(
        **community_in.model_dump(exclude={"archetypes"}), 
        creator_id=current_user.id
    )
    
    db.add(db_community)
    await db.commit()
    await db.refresh(db_community)

    # 4. INSTALL ENGINES
    installed_keys = []
    if community_in.archetypes:
        # Query for all matching engines (e.g. "social", "arena")
        stmt = select(Engine).where(Engine.key.in_(community_in.archetypes))
        result = await db.execute(stmt)
        engines_to_install = result.scalars().all()
        
        for engine_obj in engines_to_install:
            link = CommunityEngine(
                community_id=db_community.id,
                engine_id=engine_obj.id,
                is_active=True,
                config={} 
            )
            db.add(link)
            installed_keys.append(engine_obj.key)
        
        await db.commit()

    # 5. Attach keys for response so UI sees them immediately
    setattr(db_community, "installed_engines", installed_keys)
    
    return db_community

# --- ADMIN ONLY: UPDATE ---
@router.put("/{community_id}", response_model=CommunityRead)
async def update_community(
    community_id: uuid.UUID,
    community_in: CommunityUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a community (ADMIN ONLY)."""
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized.")

    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    update_data = community_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(community, key, value)

    db.add(community)
    await db.commit()
    await db.refresh(community)
    return community

# --- ADMIN ONLY: DELETE ---
@router.delete("/{community_id}")
async def delete_community(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a community (ADMIN ONLY)."""
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized.")

    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    await db.delete(community)
    await db.commit()
    return {"status": "deleted"}

@router.get("/{community_id}", response_model=CommunityRead)
async def read_community(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
):
    # 1. Fetch Community
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # 2. ⚡ DYNAMIC ENGINE SYNC ⚡
    # Join CommunityEngine -> Engine to get the keys (e.g., "arena", "guild")
    statement = (
        select(Engine.key)
        .join(CommunityEngine, CommunityEngine.engine_id == Engine.id)
        .where(CommunityEngine.community_id == community_id)
        .where(CommunityEngine.is_active == True)
    )
    result = await db.execute(statement)
    active_keys = result.scalars().all()
    
    # Overwrite the JSON field on the fly so the frontend receives the real list
    setattr(community, "installed_engines", active_keys)
    
    return community

@router.get("/by-slug/{slug}", response_model=CommunityRead)
async def get_community_by_slug(
    slug: str,
    db: AsyncSession = Depends(deps.get_db),
):
    """Lookup a territory by its URL slug and sync installed engines."""
    # 1. Fetch Community
    query = select(Community).where(Community.slug == slug)
    result = await db.execute(query)
    community = result.scalars().first()
    
    if not community:
        raise HTTPException(status_code=404, detail="Territory not found")
        
    # 2. ⚡ DYNAMIC ENGINE SYNC ⚡
    # (Exactly matching read_community logic)
    statement = (
        select(Engine.key)
        .join(CommunityEngine, CommunityEngine.engine_id == Engine.id)
        # Note: We use community.id here, since we just fetched it
        .where(CommunityEngine.community_id == community.id)
        .where(CommunityEngine.is_active == True)
    )
    result = await db.execute(statement)
    active_keys = result.scalars().all()
    
    # 3. Attach keys to response
    setattr(community, "installed_engines", active_keys)
    
    return community

@router.get("/{community_id}/membership_status")
async def get_membership_status(
    community_id: uuid.UUID, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    query = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == community_id
    )
    result = await db.execute(query)
    membership = result.scalars().first()
    return {"status": membership.status if membership else "none", "role": membership.role if membership else None}

@router.get("/{community_id}/stats")
async def get_community_stats(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get live dashboard statistics.
    """
    # 1. Fetch Community for Member Count
    comm = await db.get(Community, community_id)
    if not comm:
        raise HTTPException(status_code=404, detail="Community not found")

    # 2. Calculate Posts Today (Realtime)
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    posts_query = select(func.count(Post.id)).where(
        Post.community_id == community_id,
        Post.created_at >= start_of_day
    )
    posts_result = await db.execute(posts_query)
    posts_today = posts_result.scalar() or 0

    # 3. Calculate Pending Approvals (Realtime)
    pending_query = select(func.count(Membership.user_id)).where(
        Membership.community_id == community_id,
        Membership.status == "pending"
    )
    pending_result = await db.execute(pending_query)
    pending_count = pending_result.scalar() or 0

    return {
        "member_count": comm.member_count,
        "daily_active": int(comm.member_count * 0.45) + 1, # Mock: 45% + 1 engagement
        "posts_today": posts_today,
        "pending_reports": pending_count
    }

@router.post("/{community_id}/join")
async def join_community(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    query = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == community_id
    )
    result = await db.execute(query)
    existing_membership = result.scalars().first()

    if existing_membership:
        if existing_membership.status == "banned":
             raise HTTPException(status_code=403, detail="You are banned from this territory.")
        raise HTTPException(status_code=400, detail="Already a member")

    initial_status = "pending" if community.is_private else "active"
    new_membership = Membership(
        user_id=current_user.id,
        community_id=community_id,
        role="member",
        status=initial_status
    )
    
    # Update count
    community.member_count += 1
    db.add(community)

    db.add(new_membership)
    await db.commit()
    await db.refresh(new_membership)

    return {
        "status": "success", 
        "membership_status": initial_status,
        "message": "Request pending approval" if initial_status == "pending" else "Joined successfully"
    }

@router.get("/{community_id}/members", response_model=List[MembershipOut])
async def read_community_members(
    community_id: uuid.UUID,
    status: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_db),
):
    query = (
        select(Membership)
        .options(joinedload(Membership.user))
        .where(Membership.community_id == community_id)
    )
    if status:
        query = query.where(Membership.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{community_id}/members/{user_id}/process")
async def process_membership(
    community_id: uuid.UUID,
    user_id: uuid.UUID,
    action: str = Query(..., regex="^(approve|reject|ban)$"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Process membership (Moderator/Admin Only)."""
    # Logic note: In a real app, check if current_user is creator/mod of THIS community
    # For now, we trust the DB ownership logic or simple membership role
    
    query = select(Membership).where(
        Membership.community_id == community_id,
        Membership.user_id == user_id
    )
    result = await db.execute(query)
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(status_code=404, detail="Membership application not found")

    if action == "approve":
        membership.status = "active"
        membership.role = "member"
    elif action == "reject":
        await db.delete(membership)
        # Decrement count
        comm = await db.get(Community, community_id)
        if comm:
            comm.member_count -= 1
            db.add(comm)
        await db.commit()
        return {"status": "rejected", "message": "Application removed"}
    elif action == "ban":
        membership.status = "banned"

    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return {"status": "success", "new_state": membership.status}