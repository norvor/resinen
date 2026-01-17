from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.api import deps
from app.models.user import User
from app.models.social import Post, Comment
from app.schemas.social import PostCreate, PostRead, CommentCreate, CommentRead

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
    
    # Eager load relationships to prevent "MissingGreenlet" error
    await db.refresh(post)
    # We explicitly load author for the response
    await db.refresh(post, ["author"]) 
    
    # Return manually to ensure clean schema mapping
    return PostRead(
        **post.dict(),
        author_name=post.author.full_name,
        comments=[]
    )

@router.get("/", response_model=List[PostRead])
async def get_feed(
    community_id: UUID,
    chapter_id: UUID = None,
    limit: int = 50,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # Fetch posts with Author and Comments loaded
    query = (
        select(Post)
        .where(Post.community_id == community_id)
        .options(
            selectinload(Post.author),
            selectinload(Post.comments).selectinload(Comment.author) # Load Comment Authors too
        )
        .order_by(col(Post.created_at).desc())
        .limit(limit)
    )
    
    if chapter_id:
        query = query.where(Post.chapter_id == chapter_id)
        
    result = await db.execute(query)
    posts = result.scalars().all()

    # Map to schema
    return [
        PostRead(
            **post.dict(), 
            author_name=post.author.full_name if post.author else "Unknown",
            comments=[
                CommentRead(
                    **c.dict(),
                    author_name=c.author.full_name if c.author else "Unknown"
                ) for c in post.comments
            ]
        ) 
        for post in posts
    ]

# --- NEW ENDPOINT: COMMENTS ---
@router.post("/comments", response_model=CommentRead)
async def create_comment(
    comment_in: CommentCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # Verify post exists
    post = await db.get(Post, comment_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        **comment_in.dict(),
        author_id=current_user.id
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    # Load author so we can return the name immediately
    await db.refresh(comment, ["author"])
    
    return CommentRead(
        **comment.dict(),
        author_name=comment.author.full_name
    )