from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.arena import MatchStatus

# --- READ SCHEMAS ---
class TeamRead(BaseModel):
    id: UUID
    name: str
    logo_url: Optional[str]
    short_code: str

class MatchRead(BaseModel):
    id: UUID
    status: MatchStatus
    start_time: datetime
    
    # Teams (Nested for ease)
    team_a: TeamRead
    team_b: TeamRead
    
    # Scores
    score_a: int
    score_b: int
    time_display: str
    
    # Metadata
    total_predictions: int = 0
    pick_pct_a: int = 50 # Percentage of users who picked A
    pick_pct_b: int = 50
    
    # Did I pick?
    user_pick_id: Optional[UUID] = None

    class Config:
        from_attributes = True

# --- WRITE SCHEMAS ---
class MatchCreate(BaseModel):
    community_id: UUID
    team_a_name: str
    team_b_name: str
    start_time: datetime

class PredictionCreate(BaseModel):
    match_id: UUID
    team_id: UUID

class ScoreUpdate(BaseModel):
    score_a: int
    score_b: int
    time_display: str
    status: MatchStatus