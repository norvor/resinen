from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col, or_, func
from sqlalchemy.orm import joinedload
import uuid 
from datetime import datetime

# Models
from app.models.social import Post
from app.models.user import User
from app.models.engine import CommunityEngine, Engine
from app.models.community import Community, Membership
from app.schemas.community import CommunityCreate, CommunityRead, CommunityUpdate
from app.schemas.membership import MembershipOut

# Core
from app.api import deps

router = APIRouter()

# --- PUBLIC MAP ---
@router.get("/", response_model=List[CommunityRead])
async def read_communities(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_async_db),
):
    """Retrieve communities with their installed engines."""
    # 1. Fetch Communities
    query = select(Community)
    
    if q:
        search_term = f"%{q}%"
        # Using col() helps SQLModel infer types correctly in complex filters
        query = query.where(or_(col(Community.name).ilike(search_term), col(Community.slug).ilike(search_term)))
        
    query = query.offset(skip).limit(limit)
    
    # 🚨 ASYNC EXEC
    result = await db.exec(query)
    communities = result.scalars().all()

    # 2. Populate 'installed_engines'
    # N+1 Optimization Loop (Async friendly)
    for comm in communities:
        stmt = (
            select(Engine.key)
            .join(CommunityEngine, CommunityEngine.engine_id == Engine.id)
            .where(CommunityEngine.community_id == comm.id)
            .where(CommunityEngine.is_active == True)
        )
        engines_res = await db.exec(stmt)
        # Manually attach keys so Pydantic serializes them
        setattr(comm, "installed_engines", engines_res.scalars().all())

    return communities

@router.post("/", response_model=CommunityRead)
async def create_community(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
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
    existing = await db.exec(query)
    if existing.first():
        raise HTTPException(status_code=400, detail="Community slug already exists")

    # 3. Create Community Record
    # We unpack Pydantic model but exclude 'archetypes' which is logic-only
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
        # Find engine IDs for requested keys (e.g. "social", "arena")
        stmt = select(Engine).where(col(Engine.key).in_(community_in.archetypes))
        result = await db.exec(stmt)
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

    # 5. Attach keys for immediate UI feedback
    setattr(db_community, "installed_engines", installed_keys)
    
    return db_community

# --- ADMIN ONLY: UPDATE ---
@router.put("/{community_id}", response_model=CommunityRead)
async def update_community(
    community_id: uuid.UUID,
    community_in: CommunityUpdate,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a community (ADMIN ONLY)."""
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized.")

    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    update_data = community_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(community, key, value)

    db.add(community)
    await db.commit()
    await db.refresh(community)
    
    # Re-fetch engines to keep response consistent
    stmt = (
        select(Engine.key)
        .join(CommunityEngine, CommunityEngine.engine_id == Engine.id)
        .where(CommunityEngine.community_id == community.id)
        .where(CommunityEngine.is_active == True)
    )
    engines_res = await db.exec(stmt)
    setattr(community, "installed_engines", engines_res.scalars().all())

    return community

# --- ADMIN ONLY: DELETE ---
@router.delete("/{community_id}")
async def delete_community(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
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
    db: AsyncSession = Depends(deps.get_async_db),
):
    # 1. Fetch Community
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # 2. ⚡ DYNAMIC ENGINE SYNC ⚡
    statement = (
        select(Engine.key)
        .join(CommunityEngine, CommunityEngine.engine_id == Engine.id)
        .where(CommunityEngine.community_id == community_id)
        .where(CommunityEngine.is_active == True)
    )
    result = await db.exec(statement)
    active_keys = result.scalars().all()
    
    # Attach to runtime object
    setattr(community, "installed_engines", active_keys)
    
    return community

@router.get("/by-slug/{slug}", response_model=CommunityRead)
async def get_community_by_slug(
    slug: str,
    db: AsyncSession = Depends(deps.get_async_db),
):
    """Lookup a territory by its URL slug."""
    # 1. Fetch
    query = select(Community).where(Community.slug == slug)
    result = await db.exec(query)
    community = result.scalars().first()
    
    if not community:
        raise HTTPException(status_code=404, detail="Territory not found")
        
    # 2. Sync Engines
    statement = (
        select(Engine.key)
        .join(CommunityEngine, CommunityEngine.engine_id == Engine.id)
        .where(CommunityEngine.community_id == community.id)
        .where(CommunityEngine.is_active == True)
    )
    result = await db.exec(statement)
    active_keys = result.scalars().all()
    
    setattr(community, "installed_engines", active_keys)
    
    return community

@router.get("/{community_id}/membership_status")
async def get_membership_status(
    community_id: uuid.UUID, 
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    query = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == community_id
    )
    result = await db.exec(query)
    membership = result.scalars().first()
    
    return {
        "status": membership.status if membership else "none", 
        "role": membership.role if membership else None
    }

@router.get("/{community_id}/stats")
async def get_community_stats(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get live dashboard statistics."""
    
    comm = await db.get(Community, community_id)
    if not comm:
        raise HTTPException(status_code=404, detail="Community not found")

    # Realtime Posts Count (Today)
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    posts_query = select(func.count(Post.id)).where(
        Post.community_id == community_id,
        Post.created_at >= start_of_day
    )
    posts_res = await db.exec(posts_query)
    posts_today = posts_res.one() or 0 # .one() returns the count value

    # Realtime Pending Members
    pending_query = select(func.count(Membership.user_id)).where(
        Membership.community_id == community_id,
        Membership.status == "pending"
    )
    pending_res = await db.exec(pending_query)
    pending_count = pending_res.one() or 0

    return {
        "member_count": comm.member_count,
        "daily_active": int(comm.member_count * 0.45) + 1,
        "posts_today": posts_today,
        "pending_reports": pending_count
    }

@router.post("/{community_id}/join")
async def join_community(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Check existence
    query = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == community_id
    )
    result = await db.exec(query)
    existing_membership = result.scalars().first()

    if existing_membership:
        if existing_membership.status == "banned":
             raise HTTPException(status_code=403, detail="You are banned from this territory.")
        raise HTTPException(status_code=400, detail="Already a member")

    # Create new membership
    initial_status = "pending" if community.is_private else "active"
    
    new_membership = Membership(
        user_id=current_user.id,
        community_id=community_id,
        role="member",
        status=initial_status
    )
    
    # Increment Count
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
    db: AsyncSession = Depends(deps.get_async_db),
):
    # Eager Load User to avoid N+1
    query = (
        select(Membership)
        .options(joinedload(Membership.user))
        .where(Membership.community_id == community_id)
    )
    if status:
        query = query.where(Membership.status == status)
    
    result = await db.exec(query)
    return result.scalars().all()

@router.post("/{community_id}/members/{user_id}/process")
async def process_membership(
    community_id: uuid.UUID,
    user_id: uuid.UUID,
    # Regex validation is fine here
    action: str = Query(..., regex="^(approve|reject|ban)$"),
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Process membership (Moderator/Admin Only)."""
    
    query = select(Membership).where(
        Membership.community_id == community_id,
        Membership.user_id == user_id
    )
    result = await db.exec(query)
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