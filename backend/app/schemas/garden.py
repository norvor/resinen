from typing import Optional
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel

class HabitCreate(BaseModel):
    community_id: UUID
    title: str
    icon: str = "🌱"

class HabitRead(BaseModel):
    id: UUID
    title: str
    icon: str
    streak_current: int
    streak_best: int
    
    # Helper for UI: Did I do this today?
    is_completed_today: bool = False
    
    class Config:
        from_attributes = True

class LogEntry(BaseModel):
    log_date: date