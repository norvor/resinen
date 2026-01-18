from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.api import deps
from app.models.user import User
from app.models.community import Membership, Community

router = APIRouter()

# 1. LIST PENDING APPLICANTS (For Community Admins)
@router.get("/pending/{community_id}", response_model=List[Membership])
async def get_pending_members(
    community_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # SECURITY: Check if requester is an ADMIN of this community
    stmt = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == community_id,
        Membership.role == "admin",
        Membership.status == "active"
    )
    admin_check = await db.execute(stmt)
    if not admin_check.scalars().first():
        raise HTTPException(403, "You are not an Admin of this territory.")

    # FETCH: Get all pending memberships
    query = select(Membership).where(
        Membership.community_id == community_id,
        Membership.status == "pending"
    )
    result = await db.execute(query)
    return result.scalars().all()

# 2. APPROVE / REJECT (The Gavel)
@router.post("/{membership_id}/decide")
async def decide_membership(
    membership_id: UUID,
    decision: str, # 'approve' or 'reject'
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # 1. Get the membership application
    membership = await db.get(Membership, membership_id)
    if not membership:
        raise HTTPException(404, "Application not found")

    # 2. SECURITY: Verify requester is Admin of that community
    stmt = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == membership.community_id,
        Membership.role == "admin"
    )
    admin_check = await db.execute(stmt)
    if not admin_check.scalars().first():
        raise HTTPException(403, "You have no authority here.")

    # 3. EXECUTE DECISION
    if decision == "approve":
        membership.status = "active"
    elif decision == "reject":
        membership.status = "rejected"
    else:
        raise HTTPException(400, "Invalid decision")

    db.add(membership)
    await db.commit()
    return {"status": "success", "new_state": membership.status}