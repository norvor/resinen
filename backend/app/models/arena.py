import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"

# --- 1. THE COMPETITORS ---
class ArenaTeam(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    name: str
    logo_url: Optional[str] = None
    short_code: str # e.g. "LAL" for Lakers

# --- 2. THE MATCH ---
class ArenaMatch(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    # Teams
    team_a_id: uuid.UUID = Field(foreign_key="arenateam.id")
    team_b_id: uuid.UUID = Field(foreign_key="arenateam.id")
    
    # State
    status: MatchStatus = Field(default=MatchStatus.SCHEDULED)
    start_time: datetime
    
    # Live Data
    score_a: int = Field(default=0)
    score_b: int = Field(default=0)
    time_display: str = Field(default="00:00") # e.g. "Q4 02:30"
    
    # Relationships
    predictions: List["ArenaPrediction"] = Relationship(back_populates="match")

# --- 3. THE USER PREDICTION ---
class ArenaPrediction(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    match_id: uuid.UUID = Field(foreign_key="arenamatch.id", primary_key=True)
    
    picked_team_id: uuid.UUID # User thinks this team will win
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    match: "ArenaMatch" = Relationship(back_populates="predictions")