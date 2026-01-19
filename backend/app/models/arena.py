import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"

class ArenaTeam(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    logo_url: Optional[str] = None
    short_code: str # e.g. "TSM", "G2"

class ArenaMatch(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    team_a_id: uuid.UUID = Field(foreign_key="arenateam.id")
    team_b_id: uuid.UUID = Field(foreign_key="arenateam.id")
    
    start_time: datetime
    status: MatchStatus = Field(default=MatchStatus.SCHEDULED)
    
    score_a: int = 0
    score_b: int = 0
    time_display: str = "00:00"

    # Relationships for joining
    team_a: "ArenaTeam" = Relationship(sa_relationship_kwargs={"primaryjoin": "ArenaMatch.team_a_id==ArenaTeam.id"})
    team_b: "ArenaTeam" = Relationship(sa_relationship_kwargs={"primaryjoin": "ArenaMatch.team_b_id==ArenaTeam.id"})

class ArenaPrediction(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    match_id: uuid.UUID = Field(foreign_key="arenamatch.id", primary_key=True)
    picked_team_id: uuid.UUID