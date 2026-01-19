import uuid
from datetime import date
from pydantic import BaseModel

class HabitCreate(BaseModel):
    community_id: uuid.UUID
    title: str
    icon: str = "🌱"

class HabitRead(BaseModel):
    id: uuid.UUID
    title: str
    icon: str
    streak_current: int
    streak_best: int
    
    # UI helper (needs to be calculated in endpoint)
    is_completed_today: bool = False
    
    class Config:
        from_attributes = True

class LogEntry(BaseModel):
    log_date: date