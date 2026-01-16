from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime

# --- CONFIGURATION ---
class SiteConfig(SQLModel, table=True):
    id: str = Field(primary_key=True, default="global")
    brand_name: str = Field(default="Life Journey")
    # Keep minimal config

# --- GAME CONTENT (Static Data) ---
# This defines the "Magic Carpet" or "Farming" paths
class Journey(SQLModel, table=True):
    id: str = Field(primary_key=True) # e.g., "farming", "carpet"
    title: str
    description: str
    theme_color: str = Field(default="green-500") # UI Helper
    
    stops: List["Stop"] = Relationship(back_populates="journey")

class Stop(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    journey_id: str = Field(foreign_key="journey.id")
    order_index: int # 1, 2, 3... (The sequence)
    
    title: str # e.g., "First Sprout" or "Rome"
    description: str 
    visual_asset_url: str # URL to the image/gif for this stage
    
    journey: Optional[Journey] = Relationship(back_populates="stops")

# --- USER STATE (Minimal Tracking) ---
class UserProgress(SQLModel, table=True):
    id: str = Field(primary_key=True, default="me") 
    
    # Which journey is active?
    active_journey_id: str = Field(foreign_key="journey.id", nullable=True)
    
    # How far along are they? (0 = Start)
    current_stop_index: int = Field(default=0) 
    
    # Daily Progress (The "5 Care Tools" Logic)
    # We just count points. 5 points = Next Stop.
    daily_care_points: int = Field(default=0) 
    
    # We need this ONLY to know when to reset the daily_care_points (New Day)
    last_care_date: datetime = Field(default_factory=datetime.utcnow)