import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.community import Community, Membership # Import Membership
    from app.models.social import Post

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # --- RELATIONSHIPS ---
    posts: List["Post"] = Relationship(back_populates="author")
    
    # 1. Communities the user CREATED
    communities: List["Community"] = Relationship(back_populates="creator")
    
    # 2. Communities the user JOINED
    memberships: List["Membership"] = Relationship(back_populates="user")