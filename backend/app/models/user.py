import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# Use TYPE_CHECKING to avoid circular import errors
if TYPE_CHECKING:
    from app.models.social import Post, Comment
    from app.models.community import Community  # <--- WE NEED THIS
    from app.models.referral import MemberService, Membership

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # --- RELATIONSHIPS ---
    
    # 1. Social
    posts: List["Post"] = Relationship(back_populates="author")
    
    # 2. Communities (The Fix for your Error)
    communities: List["Community"] = Relationship(back_populates="creator")

    # 3. Services / Memberships (If you use them)
    #services: List["MemberService"] = Relationship(back_populates="user")
    memberships: List["Membership"] = Relationship(back_populates="user")