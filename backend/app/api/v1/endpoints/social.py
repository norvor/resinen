import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload, selectinload

from app.api import deps
from app.models.user import User
from app.models.social import Post, PostLike, Comment, CommentLike
from app.models.community import Membership
from app.schemas.social import PostCreate, PostRead, CommentCreate, CommentRead

router = APIRouter()

# ==========================================
# 1. POSTS (Feed & CRUD)
# ==========================================

@router.get("/feed", response_model=List[PostRead])
async def read_posts(
    community_id: uuid.UUID, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 20
):
    """Fetch feed with 'is_liked' status populated for the current user."""
    # 1. Fetch Posts
    query = (
        select(Post)
        .where(Post.community_id == community_id)
        .options(joinedload(Post.author))
        .order_by(Post.is_pinned.desc(), Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    posts = (await db.execute(query)).scalars().all()

    # 2. Populate 'is_liked' efficiently
    # Fetch all PostLike IDs for this user in this batch
    post_ids = [p.id for p in posts]
    liked_ids = set()
    if post_ids:
        like_stmt = select(PostLike.post_id).where(
            PostLike.user_id == current_user.id,
            PostLike.post_id.in_(post_ids)
        )
        liked_result = await db.execute(like_stmt)
        liked_ids = set(liked_result.scalars().all())

    # 3. Attach state
    for p in posts:
        p.is_liked = p.id in liked_ids

    return posts

@router.post("/posts", response_model=PostRead)
async def create_post(
    post_in: PostCreate, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # Membership Check
    mem = await db.execute(select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == post_in.community_id,
        Membership.status.in_(["active", "admin", "owner"])
    ))
    if not mem.scalars().first():
        raise HTTPException(403, "Must be a citizen to post.")

    new_post = Post(
        **post_in.model_dump(),
        author_id=current_user.id,
        like_count=0, view_count=0, comment_count=0
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    # Populate Author for response
    new_post.author = current_user
    new_post.is_liked = False
    return new_post

@router.get("/posts/{post_id}", response_model=PostRead)
async def get_post(
    post_id: uuid.UUID, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get single post + Increment View Count."""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
        
    # Increment View (Atomic-ish)
    post.view_count += 1
    db.add(post)
    
    # Check Like Status
    like_check = await db.get(PostLike, (current_user.id, post_id))
    post.is_liked = bool(like_check)
    
    await db.commit()
    await db.refresh(post)
    return post

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # Toggle Like
    existing = await db.get(PostLike, (current_user.id, post_id))
    post = await db.get(Post, post_id)
    if not post: raise HTTPException(404, "Post not found")

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

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    post = await db.get(Post, post_id)
    if not post: raise HTTPException(404, "Not found")
    
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(403, "Not your post.")
        
    await db.delete(post)
    await db.commit()
    return {"status": "deleted"}


# ==========================================
# 2. COMMENTS (The Missing Engine Parts)
# ==========================================

@router.get("/posts/{post_id}/comments", response_model=List[CommentRead])
async def read_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Fetch comments for a post."""
    query = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(joinedload(Comment.author))
        .order_by(Comment.created_at.asc())
    )
    comments = (await db.execute(query)).scalars().all()
    
    # Populate is_liked for comments
    comment_ids = [c.id for c in comments]
    liked_ids = set()
    if comment_ids:
        res = await db.execute(select(CommentLike.comment_id).where(
            CommentLike.user_id == current_user.id,
            CommentLike.comment_id.in_(comment_ids)
        ))
        liked_ids = set(res.scalars().all())

    for c in comments:
        c.is_liked = c.id in liked_ids
        
    return comments

@router.post("/posts/{post_id}/comments", response_model=CommentRead)
async def create_comment(
    post_id: uuid.UUID,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    post = await db.get(Post, post_id)
    if not post: raise HTTPException(404, "Post not found")

    # Create Comment
    comment = Comment(
        **comment_in.model_dump(),
        post_id=post_id,
        user_id=current_user.id
    )
    db.add(comment)
    
    # Update Post Counter
    post.comment_count += 1
    db.add(post)
    
    await db.commit()
    await db.refresh(comment)
    
    # Return with Author populated
    comment.author = current_user
    comment.is_liked = False
    return comment

@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    comment = await db.get(Comment, comment_id)
    if not comment: raise HTTPException(404, "Comment not found")
    
    existing = await db.get(CommentLike, (current_user.id, comment_id))
    
    if existing:
        await db.delete(existing)
        action = "unliked"
    else:
        db.add(CommentLike(user_id=current_user.id, comment_id=comment_id))
        action = "liked"
    
    # Recalculate count (safer than incrementing blindly)
    # Or simple increment for speed:
    # comment.like_count += 1 if action == "liked" else -1
    
    await db.commit()
    return {"status": action}

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    comment = await db.get(Comment, comment_id)
    if not comment: raise HTTPException(404)
    
    if comment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(403)
        
    # Decrement post count
    post = await db.get(Post, comment.post_id)
    if post:
        post.comment_count = max(0, post.comment_count - 1)
        db.add(post)

    await db.delete(comment)
    await db.commit()
    return {"status": "deleted"}