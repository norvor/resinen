from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# -------------------------------------------
# COMMENTS (Dependencies for Posts)
# -------------------------------------------
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: UUID

class CommentRead(CommentBase):
    id: UUID
    author_id: UUID
    author_name: Optional[str] = "Unknown" # Display name in UI
    created_at: datetime

# -------------------------------------------
# POSTS
# -------------------------------------------
class PostBase(BaseModel):
    content: str
    image_url: Optional[str] = None
    community_id: UUID
    chapter_id: Optional[UUID] = None

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: UUID
    author_id: UUID
    
    # This is the field we manually inject in the endpoint
    author_name: str 
    
    like_count: int
    created_at: datetime
    
    # Pydantic will try to read 'post.comments' from the database object.
    # Because we added .options(selectinload(Post.comments)) in the endpoint,
    # this will work perfectly now.
    comments: List[CommentRead] = []