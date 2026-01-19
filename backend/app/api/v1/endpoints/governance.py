import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, timezone

from app.api import deps
from app.models.user import User
from app.models.governance import Proposal, ProposalVote, ProposalStatus, VoteType
from app.schemas.governance import ProposalCreate, ProposalRead, VoteCreate

router = APIRouter()

# --- 1. LIST PROPOSALS ---
@router.get("/", response_model=List[ProposalRead])
async def list_proposals(
    community_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Fetch the active and past ballots for the territory."""
    
    # ✅ FIX: Use joinedload(Proposal.author) to prevent async lazy-load errors
    statement = (
        select(Proposal)
        .options(joinedload(Proposal.author))
        .where(Proposal.community_id == community_id)
        .order_by(Proposal.created_at.desc())
    )
    
    # ✅ FIX: Correct Async execution pattern
    result = await db.execute(statement)
    proposals = result.scalars().all()

    # B. Fetch User's Votes (Batch Optimized)
    prop_ids = [p.id for p in proposals]
    user_votes_map = {}
    
    if prop_ids:
        vote_stmt = select(ProposalVote).where(
            ProposalVote.user_id == current_user.id,
            ProposalVote.proposal_id.in_(prop_ids)
        )
        vote_result = await db.execute(vote_stmt)
        user_votes_map = {v.proposal_id: v.choice for v in vote_result.scalars().all()}

    # C. Assemble the Ballot Papers
    enriched = []
    now = datetime.now(timezone.utc)
    
    for p in proposals:
        # Compatibility check for model validation
        p_read = ProposalRead.model_validate(p) if hasattr(ProposalRead, "model_validate") else ProposalRead.from_orm(p)
        
        p_read.author_name = p.author.full_name if p.author else "The Architect"
        p_read.user_vote = user_votes_map.get(p.id) 
        
        # Check if the ballot has expired in real-time
        if p.status == ProposalStatus.ACTIVE and now > p.ends_at:
            p_read.status = "EXPIRED" # UI Hint
            
        enriched.append(p_read)
        
    return enriched

# --- 2. CREATE PROPOSAL ---
@router.post("/", response_model=ProposalRead)
async def create_proposal(
    prop_in: ProposalCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Draft a new legislation (Proposal) for the community to vote on."""
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=prop_in.duration_days)
    
    new_prop = Proposal(
        community_id=prop_in.community_id,
        author_id=current_user.id,
        title=prop_in.title,
        description=prop_in.description,
        ends_at=end_date,
        status=ProposalStatus.ACTIVE,
        created_at=now,
        votes_yes=0,
        votes_no=0,
        votes_abstain=0
    )
    
    db.add(new_prop)
    await db.commit()
    await db.refresh(new_prop)
    
    # Format for response
    resp = ProposalRead.model_validate(new_prop) if hasattr(ProposalRead, "model_validate") else ProposalRead.from_orm(new_prop)
    resp.author_name = current_user.full_name
    return resp

# --- 3. CAST VOTE ---
@router.post("/{proposal_id}/vote", response_model=Any)
async def cast_vote(
    proposal_id: uuid.UUID,
    vote_in: VoteCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Cast a digital ballot. One student, one vote."""
    
    # 1. Fetch Proposal logic
    prop = await db.get(Proposal, proposal_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Ballot not found")
        
    now = datetime.now(timezone.utc)
    if prop.status != ProposalStatus.ACTIVE or now > prop.ends_at:
        raise HTTPException(status_code=400, detail="Voting for this session is closed")

    # 2. Check for double-voting
    # ✅ FIX: Composite key check using explicit select for Async compatibility
    stmt = select(ProposalVote).where(
        ProposalVote.proposal_id == proposal_id,
        ProposalVote.user_id == current_user.id
    )
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="You have already cast your vote")

    # 3. Record the Vote
    new_vote = ProposalVote(
        proposal_id=proposal_id, 
        user_id=current_user.id, 
        choice=vote_in.choice
    )
    db.add(new_vote)
    
    # 4. Atomic-style Increment
    if vote_in.choice == VoteType.YES:
        prop.votes_yes += 1
    elif vote_in.choice == VoteType.NO:
        prop.votes_no += 1
    else:
        prop.votes_abstain += 1
        
    db.add(prop)
    await db.commit()
    
    return {"status": "success", "choice": vote_in.choice}