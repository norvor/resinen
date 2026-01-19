import uuid
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

# --- 1. THE HABIT (The Seed) ---
class GardenHabit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str # e.g. "Drink 2L Water"
    icon: str = Field(default="🌱")
    
    # Gamification
    streak_current: int = Field(default=0)
    streak_best: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    community: "Community" = Relationship()
    user: "User" = Relationship()
    logs: List["GardenLog"] = Relationship(back_populates="habit")

# --- 2. THE LOG (The Water) ---
class GardenLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    habit_id: uuid.UUID = Field(foreign_key="gardenhabit.id")
    
    # We store just the date to prevent duplicate checks per day
    log_date: date = Field(default_factory=date.today)
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    
    habit: "GardenHabit" = Relationship(back_populates="logs")