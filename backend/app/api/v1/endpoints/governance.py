import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.user import User
from app.models.governance import GovernanceIssue, GovernanceVote
from app.services.jury import summon_jury
from app.services.reputation import award_xp, XP_PER_JURY_VOTE

router = APIRouter()

# 1. CREATE ISSUE (Triggers Jury)
@router.post("/issues", response_model=GovernanceIssue)
async def create_issue(
    issue_in: GovernanceIssue, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    issue_in.creator_id = current_user.id
    issue_in.created_at = datetime.utcnow()
    issue_in.expires_at = datetime.utcnow() + timedelta(days=3)
    
    db.add(issue_in)
    await db.commit()
    await db.refresh(issue_in)
    
    if issue_in.kind == "moderation":
        await summon_jury(issue_in.community_id, issue_in.id, db)
        
    return issue_in

# 2. LIST ISSUES
@router.get("/issues", response_model=List[GovernanceIssue])
async def list_issues(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
):
    query = select(GovernanceIssue).where(GovernanceIssue.community_id == community_id)
    result = await db.execute(query)
    return result.scalars().all()

# 3. CAST VOTE (With XP Reward)
@router.post("/vote")
async def cast_vote(
    issue_id: uuid.UUID,
    vote_val: str, 
    reason: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # Check if user already voted or was summoned
    query = select(GovernanceVote).where(
        GovernanceVote.issue_id == issue_id,
        GovernanceVote.user_id == current_user.id
    )
    result = await db.execute(query)
    existing_vote = result.scalars().first()
    
    if existing_vote:
        if existing_vote.vote != "pending":
             raise HTTPException(400, "You have already voted.")
        # Update the pending jury vote
        existing_vote.vote = vote_val
        existing_vote.reason = reason
        db.add(existing_vote)
    else:
        # Open voting
        new_vote = GovernanceVote(
            issue_id=issue_id,
            user_id=current_user.id,
            vote=vote_val,
            reason=reason
        )
        db.add(new_vote)
        
    # REWARD THE JUROR
    await award_xp(
        user_id=current_user.id,
        amount=XP_PER_JURY_VOTE,
        source="jury_duty",
        source_id=str(issue_id),
        db=db
    )
        
    await db.commit()
    return {"status": "vote_cast"}