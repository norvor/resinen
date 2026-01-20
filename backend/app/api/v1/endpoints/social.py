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
    # 1. Fetch Posts (Database Models)
    query = (
        select(Post)
        .where(Post.community_id == community_id)
        .options(joinedload(Post.author))
        .order_by(Post.is_pinned.desc(), Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    posts_db = (await db.execute(query)).scalars().all()

    # 2. Get Like Status efficiently
    post_ids = [p.id for p in posts_db]
    liked_ids = set()
    if post_ids:
        like_stmt = select(PostLike.post_id).where(
            PostLike.user_id == current_user.id,
            PostLike.post_id.in_(post_ids)
        )
        liked_result = await db.execute(like_stmt)
        liked_ids = set(liked_result.scalars().all())

    # 3. CONVERT & ATTACH STATE (The Fix)
    results = []
    for p in posts_db:
        # Convert DB Model -> Pydantic Schema
        post_read = PostRead.model_validate(p)
        # Now we can safely add the UI state
        post_read.is_liked = (p.id in liked_ids)
        results.append(post_read)

    return results

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
    
    # Return directly (or use model_validate if you need extra computed fields)
    # We manually attach author since we just created it
    new_post.author = current_user
    
    # Convert to schema to attach is_liked
    response = PostRead.model_validate(new_post)
    response.is_liked = False
    return response

@router.get("/posts/{post_id}", response_model=PostRead)
async def get_post(
    post_id: uuid.UUID, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
        
    # Increment View
    post.view_count += 1
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    # Check Like
    like_check = await db.get(PostLike, (current_user.id, post_id))
    
    # Convert & Return
    response = PostRead.model_validate(post)
    response.is_liked = bool(like_check)
    return response

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
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
# 2. COMMENTS
# ==========================================

@router.get("/posts/{post_id}/comments", response_model=List[CommentRead])
async def read_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    query = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(joinedload(Comment.author))
        .order_by(Comment.created_at.asc())
    )
    comments_db = (await db.execute(query)).scalars().all()
    
    # Get Likes
    comment_ids = [c.id for c in comments_db]
    liked_ids = set()
    if comment_ids:
        res = await db.execute(select(CommentLike.comment_id).where(
            CommentLike.user_id == current_user.id,
            CommentLike.comment_id.in_(comment_ids)
        ))
        liked_ids = set(res.scalars().all())

    # Convert & Attach
    results = []
    for c in comments_db:
        # Fix for Comments too
        comment_read = CommentRead.model_validate(c)
        comment_read.is_liked = (c.id in liked_ids)
        results.append(comment_read)
        
    return results

@router.post("/posts/{post_id}/comments", response_model=CommentRead)
async def create_comment(
    post_id: uuid.UUID,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    post = await db.get(Post, post_id)
    if not post: raise HTTPException(404, "Post not found")

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
    
    comment.author = current_user
    
    # Return schema
    response = CommentRead.model_validate(comment)
    response.is_liked = False
    return response

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
        
    post = await db.get(Post, comment.post_id)
    if post:
        post.comment_count = max(0, post.comment_count - 1)
        db.add(post)

    await db.delete(comment)
    await db.commit()
    return {"status": "deleted"}