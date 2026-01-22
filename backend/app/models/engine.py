import uuid
from typing import Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

class Engine(SQLModel, table=True):
    __tablename__ = "engine"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str = Field(unique=True, index=True) # "journal", "vault", "brain"
    name: str
    description: str
    icon: str
    is_system: bool = Field(default=False)

class UserEngine(SQLModel, table=True):
    __tablename__ = "user_engine"
    
    # Composite Primary Key (One entry per user per engine)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    engine_id: uuid.UUID = Field(foreign_key="engine.id", primary_key=True)
    
    is_active: bool = Field(default=True)
    config: Dict[str, Any] = Field(default={}, sa_type=JSONB)