import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.arena import MatchStatus

# --- TEAMS ---
class TeamRead(BaseModel):
    id: uuid.UUID
    name: str
    logo_url: Optional[str] = None
    short_code: str
    class Config:
        from_attributes = True

# --- MATCH ---
class MatchBase(BaseModel):
    start_time: datetime
    status: MatchStatus = MatchStatus.SCHEDULED

class MatchCreate(MatchBase):
    community_id: uuid.UUID
    team_a_id: uuid.UUID
    team_b_id: uuid.UUID

class MatchRead(MatchBase):
    id: uuid.UUID
    community_id: uuid.UUID
    
    score_a: int
    score_b: int
    time_display: str
    
    # Returning full objects for UI convenience
    team_a: TeamRead
    team_b: TeamRead
    
    class Config:
        from_attributes = True

# --- PREDICTION ---
class PredictionCreate(BaseModel):
    match_id: uuid.UUID
    team_id: uuid.UUID

class ScoreUpdate(BaseModel):
    score_a: int
    score_b: int
    time_display: str
    status: MatchStatus