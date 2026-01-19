import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class ProposalStatus(str, Enum):
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"

class VoteType(str, Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

class Proposal(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    status: ProposalStatus = Field(default=ProposalStatus.ACTIVE)
    
    votes_yes: int = 0
    votes_no: int = 0
    votes_abstain: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ends_at: datetime

class ProposalVote(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    proposal_id: uuid.UUID = Field(foreign_key="proposal.id", primary_key=True)
    choice: VoteType