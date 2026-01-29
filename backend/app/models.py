from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, JSON
from datetime import datetime

# --- USER ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_premium: bool = Field(default=False)
    country_code: str = Field(default="IN")
    data_consent: bool = Field(default=False)
    marketing_consent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (One-to-One / One-to-Many)
    budget: Optional["BudgetWidget"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    habits: Optional["HabitWidget"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    scribble: Optional["ScribbleWidget"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    travel: Optional["TravelWidget"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    
    tasks: List["TaskWidget"] = Relationship(back_populates="user")
    notes: List["NoteWidget"] = Relationship(back_populates="user")
    loves: List["LoveWidget"] = Relationship(back_populates="user")
    transmission: List["TransmissionWidget"] = Relationship(back_populates="user")

# --- WIDGETS ---

class BudgetWidget(SQLModel, table=True):
    __tablename__ = "budget_widget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    monthly_limit: int = Field(default=50000)
    spent: int = Field(default=0)
    currency: str = Field(default="INR")
    user: Optional[User] = Relationship(back_populates="budget")

class HabitWidget(SQLModel, table=True):
    __tablename__ = "habit_widget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    # Stores the 2D grid or list of habits as JSON
    grid_data: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    user: Optional[User] = Relationship(back_populates="habits")

class ScribbleWidget(SQLModel, table=True):
    __tablename__ = "scribble_widget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content: str = Field(default="")
    user: Optional[User] = Relationship(back_populates="scribble")

class TravelWidget(SQLModel, table=True):
    __tablename__ = "travel_widget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    # FIX: Explicitly naming it 'places' to match frontend/router
    places: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    user: Optional[User] = Relationship(back_populates="travel")

class TaskWidget(SQLModel, table=True):
    __tablename__ = "task_widget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    # FIX: Using 'content' to match router
    content: str 
    is_done: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="tasks")

class NoteWidget(SQLModel, table=True):
    __tablename__ = "note_widget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    content: str
    is_pinned: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="notes")

class LoveWidget(SQLModel, table=True):
    __tablename__ = "love_widget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    category: str # book, movie, person
    description: Optional[str] = None
    link: Optional[str] = None # Added link field
    user: Optional[User] = Relationship(back_populates="loves")

class TransmissionWidget(SQLModel, table=True):
    __tablename__ = "transmission_widget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    url: str
    type: str # video, music, article
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="transmission")

class Mission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    
    # The Identity
    codename: str  # e.g., "PROJECT_TITAN"
    rune: str      # e.g., "🚀"
    color: str     # e.g., "#ef4444" (Red), "#3b82f6" (Blue)
    
    # The State
    status: str = "ACTIVE" # ACTIVE, STEALTH, COMPLETED, ABORTED
    progress: int = 0      # 0 to 100
    
    # The Intel
    briefing: str = ""     # Markdown description of the mission
    deadline: Optional[str] = None
    
    # System Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

# --- BLOG / CMS (Future Use) ---
class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True)
    title: str
    content: str
    author: str
    published: bool = Field(default=False)
