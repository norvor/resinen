import uuid
from typing import Dict
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column

class UserEngine(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    engine_id: uuid.UUID = Field(foreign_key="engine.id", primary_key=True)
    
    is_active: bool = True
    is_pinned: bool = Field(default=False)
    config: Dict = Field(default={}, sa_column=Column(JSON))