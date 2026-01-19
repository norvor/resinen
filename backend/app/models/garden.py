import uuid
from datetime import date
from sqlmodel import Field, SQLModel

class GardenHabit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    icon: str = "🌱"
    
    streak_current: int = 0
    streak_best: int = 0

class GardenLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    habit_id: uuid.UUID = Field(foreign_key="gardenhabit.id")
    log_date: date = Field(default_factory=date.today)