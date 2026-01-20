from uuid import UUID
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel
from app.models.arena import MatchStatus

# =======================
# 1. TEAMS
# =======================
class ArenaTeamBase(SQLModel):
    name: str
    logo_url: Optional[str] = None
    color: str = "#000000"

class ArenaTeamCreate(ArenaTeamBase):
    pass

class ArenaTeamRead(ArenaTeamBase):
    id: UUID
    community_id: UUID


# =======================
# 2. MATCHES
# =======================
class ArenaMatchBase(SQLModel):
    team_a_id: UUID
    team_b_id: UUID
    start_time: datetime
    status: MatchStatus = MatchStatus.SCHEDULED
    score_a: int = 0
    score_b: int = 0
    time_display: str = "00:00"

class ArenaMatchCreate(ArenaMatchBase):
    pass

# The "Read" model needs to include the nested Team objects
# so the Frontend can show "Red Dragons" instead of "uuid-1234"
class ArenaMatchRead(ArenaMatchBase):
    id: UUID
    community_id: UUID
    team_a: Optional[ArenaTeamRead] = None
    team_b: Optional[ArenaTeamRead] = None


# =======================
# 3. ACTIONS (Predict & Score)
# =======================
class ArenaPredictionCreate(SQLModel):
    match_id: UUID
    team_id: UUID

class ArenaScoreUpdate(SQLModel):
    score_a: Optional[int] = None
    score_b: Optional[int] = None
    status: Optional[MatchStatus] = None
    time_display: Optional[str] = None