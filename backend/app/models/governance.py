import uuid
from datetime import datetime, timedelta
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

# --- ENUMS ---
class ProposalStatus(str, Enum):
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"

class VoteType(str, Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

# --- 1. RULES & BYLAWS (The Missing Classes) ---
class PlatformRule(SQLModel, table=True):
    """
    The Constitution. These are the 'Hard Rules' set by Resinen.
    No community can disable these.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str              # e.g., "Zero Tolerance for Violence"
    description: str        # "Any threat of physical harm..."
    severity: str           # "critical" (immediate ban), "warning"
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityBylaw(SQLModel, table=True):
    """
    The Local Laws. These are specific to a 'Social Media' (Community).
    e.g., 'Sikh History Group' might ban 'Political Debates'.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    rule_key: str           # "allow_politics", "allow_nsfw"
    rule_value: str         # "false", "true", "restricted"
    description: str        
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- 2. THE PROPOSAL ---
class Proposal(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    
    # State
    status: ProposalStatus = Field(default=ProposalStatus.ACTIVE)
    
    # Counts (Denormalized for speed)
    votes_yes: int = Field(default=0)
    votes_no: int = Field(default=0)
    votes_abstain: int = Field(default=0)
    
    # Timers
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ends_at: datetime

    # Relationships
    community: "Community" = Relationship()
    author: "User" = Relationship()

# --- 3. THE VOTE RECORD ---
class ProposalVote(SQLModel, table=True):
    proposal_id: uuid.UUID = Field(foreign_key="proposal.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    
    choice: VoteType
    created_at: datetime = Field(default_factory=datetime.utcnow)