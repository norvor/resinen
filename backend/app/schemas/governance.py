from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.governance import ProposalStatus, VoteType

# --- CREATE ---
class ProposalCreate(BaseModel):
    community_id: UUID
    title: str
    description: str
    duration_days: int = 3 # Optional override

# --- READ ---
class ProposalRead(BaseModel):
    id: UUID
    community_id: UUID
    author_id: UUID
    author_name: Optional[str] = None # Enriched
    
    title: str
    description: str
    status: ProposalStatus
    
    votes_yes: int
    votes_no: int
    votes_abstain: int
    
    created_at: datetime
    ends_at: datetime
    
    # Has the current user voted? (Frontend needs this)
    user_vote: Optional[VoteType] = None

    class Config:
        from_attributes = True

# --- ACTION ---
class VoteCreate(BaseModel):
    choice: VoteType