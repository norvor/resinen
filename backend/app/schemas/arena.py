import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.models.arena import MatchStatus

# --- TEAMS ---
class ArenaTeamBase(SQLModel):
    name: str
    logo_url: Optional[str] = None
    color: str = "#000000"

class ArenaTeamCreate(ArenaTeamBase):
    pass

class ArenaTeamRead(ArenaTeamBase):
    id: uuid.UUID
    community_id: uuid.UUID

# --- MATCHES ---
class ArenaMatchBase(SQLModel):
    team_a_id: uuid.UUID
    team_b_id: uuid.UUID
    score_a: int = 0
    score_b: int = 0
    status: MatchStatus = MatchStatus.SCHEDULED
    start_time: datetime
    time_display: str = "00:00"

class ArenaMatchCreate(ArenaMatchBase):
    pass

class ArenaMatchRead(ArenaMatchBase):
    id: uuid.UUID
    community_id: uuid.UUID
    # We include team details for the dashboard
    team_a: ArenaTeamRead
    team_b: ArenaTeamRead

# --- ACTIONS ---
class ArenaPredictionCreate(SQLModel):
    match_id: uuid.UUID
    team_id: uuid.UUID

class ArenaScoreUpdate(SQLModel):
    score_a: Optional[int] = None
    score_b: Optional[int] = None
    status: Optional[MatchStatus] = None
    time_display: Optional[str] = None