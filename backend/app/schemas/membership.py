from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

# 1. Define what User details are safe to share (No passwords!)
class UserInMembership(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True

# 2. Define the Membership output that INCLUDES the User
class MembershipOut(BaseModel):
    id: UUID
    user_id: UUID
    community_id: UUID
    role: str
    status: str
    joined_at: datetime
    
    # This is the magic field. If this is missing, the API drops the data.
    user: Optional[UserInMembership] = None 

    class Config:
        from_attributes = True