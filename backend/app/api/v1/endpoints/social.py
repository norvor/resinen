import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.user import User
# FIX 1: Import 'Comment' so we can use it in the query
from app.models.social import Post, PostLike, Comment 
from app.models.community import Membership
from app.models.governance import CommunityBylaw
from app.services.reputation import award_xp, XP_PER_LIKE
from app.schemas.social import PostCreate, PostRead, CommentRead

router = APIRouter()

# ==========================================
# 1. GET FEED (The Fix)
# ==========================================
@router.get("/feed", response_model=List[PostRead])
async def read_posts(
    # 🚨 THIS NAME MUST MATCH THE URL QUERY PARAM (?community_id=...)
    community_id: uuid.UUID, 
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20
):
    """
    Fetch posts for a community. 
    Expects URL: /api/v1/social/feed?community_id=123...
    """
    query = (
        select(Post)
        .where(Post.community_id == community_id)
        .options(joinedload(Post.author)) # Join author so we see names
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

# --- 2. CREATE POST ---
@router.post("/posts", response_model=PostRead)
async def create_post(
    post_in: PostCreate, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # Check Membership
    membership_check = await db.execute(select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == post_in.community_id,
        Membership.status == "active"
    ))
    if not membership_check.scalars().first():
        raise HTTPException(403, "You are not a citizen of this territory.")

    new_post = Post(
        **post_in.dict(),
        author_id=current_user.id,
        like_count=0, view_count=0
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    return PostRead(
        id=new_post.id, community_id=new_post.community_id, chapter_id=new_post.chapter_id,
        title=new_post.title, content=new_post.content, image_url=new_post.image_url, link_url=new_post.link_url,
        is_pinned=False, like_count=0, comment_count=0, view_count=0, created_at=new_post.created_at,
        author_id=current_user.id, 
        author_name=current_user.full_name or "Me",
        is_liked=False, comments=[]
    )

@router.get("/posts/{post_id}", response_model=PostRead)
async def get_post(
    post_id: uuid.UUID, 
    db: AsyncSession = Depends(deps.get_db)
):
    """Get a single post with all its comments."""
    
    # We load the author, the comments, AND the authors of those comments
    stmt = (
        select(Post)
        .options(
            joinedload(Post.author),
            selectinload(Post.comments).joinedload(Comment.author)
        )
        .where(Post.id == post_id)
    )
    
    result = await db.execute(stmt)
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    return post


# --- 3. LIKE POST ---
@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    existing = await db.execute(select(PostLike).where(
        PostLike.user_id == current_user.id,
        PostLike.post_id == post_id
    ))
    if existing.scalars().first():
        return {"status": "already_liked"}

    new_like = PostLike(user_id=current_user.id, post_id=post_id)
    db.add(new_like)
    
    post = await db.get(Post, post_id)
    if post:
        post.like_count += 1
        db.add(post)
    
    await db.commit()
    return {"status": "liked"}

# 1. DELETE POST
@router.delete("/posts/{post_id}", response_model=Any)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Permanently delete a post."""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    
    # Optional: Check if user is author or admin
    # if post.author_id != current_user.id:
    #     raise HTTPException(403, "Not authorized")

    await db.delete(post)
    await db.commit()
    return {"status": "success"}

# 2. PIN/UNPIN POST
@router.post("/posts/{post_id}/pin", response_model=PostRead)
async def toggle_pin_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Toggle the pinned status of a post."""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
        
    # Toggle the boolean
    post.is_pinned = not post.is_pinned
    
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post