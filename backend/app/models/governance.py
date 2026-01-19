import uuid
from datetime import datetime, timedelta
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

class ProposalStatus(str, Enum):
    DRAFT = "draft"       # Needs 'seconds' to activate
    ACTIVE = "active"     # Open for voting
    PASSED = "passed"     # Vote succeeded
    FAILED = "failed"     # Vote failed
    REJECTED = "rejected" # Did not get enough seconds

class VoteType(str, Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

# --- THE PROPOSAL ---
class Proposal(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    
    # State
    status: ProposalStatus = Field(default=ProposalStatus.ACTIVE) # MVP: Skip "Draft" phase for now
    
    # Counts (Denormalized for speed)
    votes_yes: int = Field(default=0)
    votes_no: int = Field(default=0)
    votes_abstain: int = Field(default=0)
    
    # Timers
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ends_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=3)) # Default 3 day vote

    # Relationships
    community: "Community" = Relationship()
    author: "User" = Relationship()

# --- THE VOTE RECORD ---
class ProposalVote(SQLModel, table=True):
    proposal_id: uuid.UUID = Field(foreign_key="proposal.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    
    choice: VoteType
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityBylaw(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)