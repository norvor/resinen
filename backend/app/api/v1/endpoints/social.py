import uuid
import json
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, desc, col
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.user import User
from app.models.community import Membership
from app.models.social import Post, PostLike, Comment, CommentLike
from app.schemas.social import PostCreate, PostRead, CommentCreate, CommentRead, FeedResult
from app.core.database import redis_client

router = APIRouter()

# ==========================================
# HELPER: Batch Hydration (Async Version)
# ==========================================
async def _populate_post_states(db: AsyncSession, posts: List[Post], user: User) -> List[PostRead]:
    """
    Takes raw DB posts and efficiently populates 'is_liked' state for the user.
    """
    if not posts:
        return []

    post_ids = [p.id for p in posts]
    
    # 1. Fetch all likes for these posts by this user in ONE query
    statement = select(PostLike.post_id).where(
        PostLike.user_id == user.id,
        col(PostLike.post_id).in_(post_ids)
    )
    result = await db.exec(statement)
    liked_ids = set(result.all())

    # 2. Convert and Attach
    results = []
    for p in posts:
        # Convert to Pydantic
        p_read = PostRead.model_validate(p)
        p_read.is_liked = (p.id in liked_ids)
        
        # Ensure author is attached (if eager loaded)
        # SQLModel sometimes needs help mapping the relationship to the Pydantic model
        if p.author:
             p_read.author = p.author
             
        results.append(p_read)
        
    return results

# ==========================================
# 1. FEED (Async)
# ==========================================

@router.get("/feed", response_model=FeedResult)
async def get_feed(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    community_id: uuid.UUID,
    cursor: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    High-performance infinite feed.
    """
    # A. REDIS (Skipped for safety in this snippet, add back if using aioredis)
    # If using standard redis-py, it blocks, so we skip for strict async compliance here.

    # B. DB QUERY
    query = (
        select(Post)
        .where(Post.community_id == community_id)
        .options(selectinload(Post.author)) # Efficiently load authors
        .order_by(desc(Post.created_at))
        .limit(limit)
    )

    # C. Execute Query
    result = await db.exec(query)
    posts = result.all()

    # D. HYDRATE (Attach is_liked)
    posts_hydrated = await _populate_post_states(db, posts, current_user)

    # E. Next Cursor Logic (Simple Timestamp or ID based)
    next_cursor = None
    if posts and len(posts) == limit:
        next_cursor = str(posts[-1].id) # Simple ID cursor for now

    return {
        "items": posts_hydrated,
        "next_cursor": next_cursor
    }


# ==========================================
# 2. POST CRUD (Async)
# ==========================================

@router.post("/posts", response_model=PostRead)
async def create_post(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    post_in: PostCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    # 1. Permission Check
    stmt = select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == post_in.community_id,
        col(Membership.status).in_(["active", "admin", "owner"])
    )
    result = await db.exec(stmt)
    mem = result.first()
    
    if not mem:
        # For dev/seeding, we might allow admins even if not explicitly joined, 
        # but strict logic requires membership:
        if not current_user.is_superuser:
            raise HTTPException(403, "Must be a citizen to post.")

    # 2. Create
    post = Post(
        **post_in.model_dump(),
        author_id=current_user.id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)

    # 3. Return
    # Attach author manually for response since we didn't eager load it
    post.author = current_user 
    return PostRead.model_validate(post)


@router.get("/posts/{post_id}", response_model=PostRead)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    # Fetch post with author
    query = select(Post).where(Post.id == post_id).options(selectinload(Post.author))
    result = await db.exec(query)
    post = result.first()
    
    if not post:
        raise HTTPException(404, "Post not found")
    
    # Increment Views
    post.view_count += 1
    db.add(post)
    await db.commit()
    
    # Check Like
    like_stmt = select(PostLike).where(
        PostLike.user_id == current_user.id, 
        PostLike.post_id == post_id
    )
    like_result = await db.exec(like_stmt)
    is_liked = like_result.first() is not None
    
    response = PostRead.model_validate(post)
    response.is_liked = is_liked
    return response


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Not found")
        
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(403, "Not your post.")
        
    await db.delete(post)
    await db.commit()
    
    return {"status": "deleted"}


# ==========================================
# 3. INTERACTIONS (Likes) - Async
# ==========================================

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    # Check existence
    stmt = select(PostLike).where(
        PostLike.user_id == current_user.id,
        PostLike.post_id == post_id
    )
    result = await db.exec(stmt)
    existing = result.first()
    
    if existing:
        await db.delete(existing)
        post.like_count = max(0, post.like_count - 1)
        action = "unliked"
    else:
        new_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        post.like_count += 1
        action = "liked"
    
    db.add(post)
    await db.commit()
    
    return {"status": action, "likes": post.like_count}


# ==========================================
# 4. COMMENTS (Async)
# ==========================================

@router.get("/posts/{post_id}/comments", response_model=List[CommentRead])
async def read_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    query = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc())
    )
    result = await db.exec(query)
    comments = result.all()
    
    # Batch Like Check
    comment_ids = [c.id for c in comments]
    liked_ids = set()
    if comment_ids:
        stmt = select(CommentLike.comment_id).where(
            CommentLike.user_id == current_user.id,
            col(CommentLike.comment_id).in_(comment_ids)
        )
        res = await db.exec(stmt)
        liked_ids = set(res.all())
        
    results = []
    for c in comments:
        c_read = CommentRead.model_validate(c)
        c_read.is_liked = (c.id in liked_ids)
        results.append(c_read)
        
    return results


@router.post("/posts/{post_id}/comments", response_model=CommentRead)
async def create_comment(
    post_id: uuid.UUID,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    comment = Comment(
        **comment_in.model_dump(),
        post_id=post_id,
        user_id=current_user.id
    )
    db.add(comment)
    
    post.comment_count += 1
    db.add(post)
    
    await db.commit()
    await db.refresh(comment)
    
    # Manual attach author
    comment.author = current_user
    return CommentRead.model_validate(comment)


@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Not found")
        
    stmt = select(CommentLike).where(
        CommentLike.user_id == current_user.id, 
        CommentLike.comment_id == comment_id
    )
    result = await db.exec(stmt)
    existing = result.first()
    
    if existing:
        await db.delete(existing)
        action = "unliked"
    else:
        db.add(CommentLike(user_id=current_user.id, comment_id=comment_id))
        action = "liked"
        
    await db.commit()
    return {"status": action}