from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from sqlalchemy.orm import selectinload # <--- IMPORTANT IMPORT
from uuid import UUID

from app.api import deps
from app.models.user import User
from app.models.social import Post
from app.schemas.social import PostCreate, PostRead

router = APIRouter()

@router.post("/", response_model=PostRead)
async def create_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    post = Post(
        **post_in.dict(),
        author_id=current_user.id
    )
    db.add(post)
    await db.commit()
    
    # FIX: We refresh the post and explicitly load the relationships
    # This prevents the "MissingGreenlet" error
    await db.refresh(post)
    
    # We must construct the response manually or ensure relationships are loaded
    # For a new post, we know comments are empty, but Pydantic might still check.
    return PostRead(
        **post.dict(),
        author_name=current_user.full_name, # We know the author is the current user
        comments=[] # Initialize empty list for new post
    )

@router.get("/", response_model=List[PostRead])
async def get_feed(
    community_id: UUID,
    chapter_id: UUID = None,
    limit: int = 50,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # FIX: We use selectinload to fetch author AND comments in one go
    query = (
        select(Post)
        .where(Post.community_id == community_id)
        .options(
            selectinload(Post.author),   # Load Author
            selectinload(Post.comments)  # Load Comments (Fixes your error)
        )
        .order_by(col(Post.created_at).desc())
        .limit(limit)
    )
    
    if chapter_id:
        query = query.where(Post.chapter_id == chapter_id)
        
    result = await db.execute(query)
    posts = result.scalars().all()

    # Manual mapping is safest to avoid accidental lazy loads
    return [
        PostRead(
            **post.dict(), 
            author_name=post.author.full_name if post.author else "Unknown",
            # If your Schema expects comments, we pass them here.
            # If not, this line is harmless.
        ) 
        for post in posts
    ]