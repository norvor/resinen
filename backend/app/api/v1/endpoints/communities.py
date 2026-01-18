from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload
import uuid

from app.api import deps
from app.models.user import User
from app.models.community import Community, Membership
from app.schemas.community import CommunityCreate, CommunityRead, CommunityUpdate
from app.schemas.membership import MembershipOut

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

@router.get("/by-slug/{slug}", response_model=Community)
async def get_community_by_slug(
    slug: str,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Lookup a territory by its URL slug (e.g., 'iron-fortress')
    """
    # 1. Search DB for the slug
    query = select(Community).where(Community.slug == slug)
    result = await db.execute(query)
    community = result.scalars().first()
    
    # 2. If not found, throw error
    if not community:
        raise HTTPException(status_code=404, detail="Territory not found")
        
    return community

# --- 2. THE MEMBERSHIP (Join/Leave) ---


    
@router.get("/{community_id}/membership_status")
async def get_membership_status(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Check if I am already a citizen here.
    """
    query = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == community_id
    )
    result = await db.execute(query)
    membership = result.scalars().first()
    return {"status": membership.status if membership else "none", "role": membership.role if membership else None}

@router.post("/{community_id}/join")
async def join_community(
    community_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # 1. Fetch Community
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # 2. FIX: Check for existing membership using 'select' instead of 'get'
    # We query the table manually because we are looking up by Foreign Keys, not Primary Key.
    query = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == community_id
    )
    result = await db.execute(query)
    existing_membership = result.scalars().first()

    if existing_membership:
        # Optional: specific error if they are banned
        if existing_membership.status == "banned":
             raise HTTPException(status_code=403, detail="You are banned from this territory.")
        raise HTTPException(status_code=400, detail="Already a member")

    # 3. Determine Status (Gatekeeping Logic)
    initial_status = "pending" if community.is_private else "active"

    # 4. Create Membership
    new_membership = Membership(
        user_id=current_user.id,
        community_id=community_id,
        role="member",
        status=initial_status
    )

    db.add(new_membership)
    await db.commit()
    await db.refresh(new_membership)

    return {
        "status": "success", 
        "membership_status": initial_status,
        "message": "Request pending approval" if initial_status == "pending" else "Joined successfully"
    }

    # 5. Return a helpful message so the Frontend knows what to show
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
    """
    Get members and include their public User profile data.
    """
    # 1. The Database Query (Must use joinedload)
    query = (
        select(Membership)
        .options(joinedload(Membership.user))  # Fetches the user data from DB
        .where(Membership.community_id == community_id)
    )
    
    if status:
        query = query.where(Membership.status == status)
    
    result = await db.execute(query)
    members = result.scalars().all()
    
    # 2. Return standard objects; FastAPI will use MembershipOut to serialize 'user'
    return members

@router.post("/{community_id}/members/{user_id}/process")
async def process_membership(
    community_id: uuid.UUID,
    user_id: uuid.UUID,
    action: str = Query(..., regex="^(approve|reject|ban)$"), # Enforce valid actions
    db: AsyncSession = Depends(deps.get_db),
    # current_user: User = Depends(deps.get_current_active_user), # Uncomment to secure
):
    """
    Process a membership application.
    Action must be: 'approve', 'reject', or 'ban'.
    """
    # 1. Find the specific membership application
    query = select(Membership).where(
        Membership.community_id == community_id,
        Membership.user_id == user_id
    )
    result = await db.execute(query)
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(status_code=404, detail="Membership application not found")

    # 2. Execute the Decision
    if action == "approve":
        membership.status = "active"
        membership.role = "member" # Ensure they have a standard role
        # Optional: membership.joined_at = datetime.utcnow()
        
    elif action == "reject":
        # Hard Delete: Remove the row so they can try again later?
        # OR Soft Delete: Set status to 'rejected'
        await db.delete(membership)
        await db.commit()
        return {"status": "rejected", "message": "Application removed"}
        
    elif action == "ban":
        membership.status = "banned"

    # 3. Save Changes
    db.add(membership)
    await db.commit()
    await db.refresh(membership)

    return {"status": "success", "new_state": membership.status}