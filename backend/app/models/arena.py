import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User

class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"

# --- TEAMS ---
class ArenaTeam(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    name: str
    logo_url: Optional[str] = None
    color: str = "#000000"
    
    # Relationships
    home_matches: List["ArenaMatch"] = Relationship(back_populates="team_a", sa_relationship_kwargs={"primaryjoin": "ArenaTeam.id==ArenaMatch.team_a_id"})
    away_matches: List["ArenaMatch"] = Relationship(back_populates="team_b", sa_relationship_kwargs={"primaryjoin": "ArenaTeam.id==ArenaMatch.team_b_id"})

# --- MATCHES ---
class ArenaMatch(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    team_a_id: uuid.UUID = Field(foreign_key="arenateam.id")
    team_b_id: uuid.UUID = Field(foreign_key="arenateam.id")
    
    score_a: int = 0
    score_b: int = 0
    status: MatchStatus = Field(default=MatchStatus.SCHEDULED)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    time_display: str = "00:00" # e.g. "45:00", "FT"

    # Relationships
    team_a: ArenaTeam = Relationship(sa_relationship_kwargs={"primaryjoin": "ArenaMatch.team_a_id==ArenaTeam.id"}, back_populates="home_matches")
    team_b: ArenaTeam = Relationship(sa_relationship_kwargs={"primaryjoin": "ArenaMatch.team_b_id==ArenaTeam.id"}, back_populates="away_matches")

# --- PREDICTIONS ---
class ArenaPrediction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    match_id: uuid.UUID = Field(foreign_key="arenamatch.id")
    picked_team_id: uuid.UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)