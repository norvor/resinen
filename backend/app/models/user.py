import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Deferred relationship import to avoid circular dependency
    posts: List["Post"] = Relationship(back_populates="author")
    services: List["MemberService"] = Relationship(back_populates="user")
    memberships: List["Membership"] = Relationship(back_populates="user")