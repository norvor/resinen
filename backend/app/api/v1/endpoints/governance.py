from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.core.database import get_session
from app.models.user import User
from app.models.governance import Proposal, ProposalVote, ProposalStatus, VoteType
from app.schemas.governance import ProposalCreate, ProposalRead, VoteCreate
from app.api.deps import get_current_user

router = APIRouter()

# 1. LIST PROPOSALS
@router.get("/", response_model=List[ProposalRead])
async def list_proposals(
    community_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Fetch Proposals
    statement = select(Proposal).where(Proposal.community_id == community_id).order_by(Proposal.created_at.desc())
    results = await db.exec(statement)
    proposals = results.all()

    # Fetch User's Votes for these proposals (Optimization: One query instead of N)
    # Get all vote records for this user in this list of proposals
    prop_ids = [p.id for p in proposals]
    vote_stmt = select(ProposalVote).where(
        ProposalVote.user_id == current_user.id,
        ProposalVote.proposal_id.in_(prop_ids)
    )
    user_votes_res = await db.exec(vote_stmt)
    user_votes_map = {v.proposal_id: v.choice for v in user_votes_res.all()}

    # Enrich Response
    enriched = []
    for p in proposals:
        # Check simple expiry logic
        if p.status == ProposalStatus.ACTIVE and datetime.utcnow() > p.ends_at:
            # Auto-close logic could go here, but for read-only we just report it
            pass 
            
        p_read = ProposalRead.from_orm(p)
        p_read.author_name = p.author.full_name if p.author else "Unknown"
        p_read.user_vote = user_votes_map.get(p.id) # Inject "yes/no" if they voted
        enriched.append(p_read)
        
    return enriched

# 2. CREATE PROPOSAL
@router.post("/", response_model=ProposalRead)
async def create_proposal(
    prop_in: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    end_date = datetime.utcnow() + timedelta(days=prop_in.duration_days)
    
    new_prop = Proposal(
        community_id=prop_in.community_id,
        author_id=current_user.id,
        title=prop_in.title,
        description=prop_in.description,
        ends_at=end_date,
        status=ProposalStatus.ACTIVE
    )
    
    db.add(new_prop)
    await db.commit()
    await db.refresh(new_prop)
    
    # Manual enrich for return
    resp = ProposalRead.from_orm(new_prop)
    resp.author_name = current_user.full_name
    return resp

# 3. CAST VOTE
@router.post("/{proposal_id}/vote", response_model=Any)
async def cast_vote(
    proposal_id: str,
    vote_in: VoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Check Exists
    prop = await db.get(Proposal, proposal_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found")
        
    if prop.status != ProposalStatus.ACTIVE or datetime.utcnow() > prop.ends_at:
        raise HTTPException(status_code=400, detail="Voting is closed")

    # Check Duplicate
    existing = await db.get(ProposalVote, (proposal_id, current_user.id))
    if existing:
        raise HTTPException(status_code=400, detail="Already voted")

    # Record Vote
    new_vote = ProposalVote(
        proposal_id=proposal_id, 
        user_id=current_user.id, 
        choice=vote_in.choice
    )
    db.add(new_vote)
    
    # Update Counts (Atomic increment not supported in plain SQLModel, using logic)
    if vote_in.choice == VoteType.YES:
        prop.votes_yes += 1
    elif vote_in.choice == VoteType.NO:
        prop.votes_no += 1
    else:
        prop.votes_abstain += 1
        
    db.add(prop)
    await db.commit()
    
    return {"status": "success", "choice": vote_in.choice}