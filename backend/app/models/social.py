from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col, desc
import uuid

from app.api import deps
from app.models.user import User
from app.models.social import Post, PostLike, Comment, CommentLike
from app.models.community import Community
from app.schemas.social import PostCreate, PostRead, CommentCreate, CommentRead

router = APIRouter()

# --- FEED & POSTS ---

@router.get("/feed", response_model=List[PostRead])
async def read_feed(
    scope: str = Query("global", regex="^(global|community)$"),
    community_id: Optional[uuid.UUID] = None,
    limit: int = 50,
    skip: int = 0,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get the social feed.
    Scope: 'global' (all public posts) or 'community' (specific territory).
    """
    # 1. Base Query joining Author for profile data
    query = (
        select(Post, User)
        .join(User, Post.author_id == User.id)
        .order_by(desc(Post.created_at))
        .offset(skip)
        .limit(limit)
    )

    # 2. Apply Scope Filters
    if scope == "community":
        if not community_id:
            raise HTTPException(status_code=400, detail="Community ID required for community scope")
        query = query.where(Post.community_id == community_id)
    
    results = await db.execute(query)
    rows = results.all()

    # 3. Optimised Like Check (Batch fetch)
    post_ids = [row.Post.id for row in rows]
    my_likes = set()
    if post_ids:
        likes_query = select(PostLike.post_id).where(
            PostLike.user_id == current_user.id,
            col(PostLike.post_id).in_(post_ids)
        )
        likes_result = await db.execute(likes_query)
        my_likes = set(likes_result.scalars().all())

    # 4. Construct Response
    posts_out = []
    for post, author in rows:
        posts_out.append(PostRead(
            id=post.id,
            content=post.content,
            image_url=post.image_url,
            link_url=post.link_url,
            title=post.title,
            community_id=post.community_id,
            chapter_id=post.chapter_id,
            created_at=post.created_at,
            like_count=post.like_count,
            comment_count=post.comment_count,
            is_liked=(post.id in my_likes),
            author_id=author.id,
            author_name=author.full_name,
            author_avatar=author.avatar_url,
            author_level=author.level
        ))
    
    return posts_out

@router.post("/posts", response_model=PostRead)
async def create_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new post."""
    post = Post(
        **post_in.dict(),
        author_id=current_user.id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    # Return formatted with user info
    return PostRead(
        id=post.id,
        content=post.content,
        image_url=post.image_url,
        link_url=post.link_url,
        title=post.title,
        community_id=post.community_id,
        chapter_id=post.chapter_id,
        created_at=post.created_at,
        like_count=0,
        comment_count=0,
        is_liked=False,
        author_id=current_user.id,
        author_name=current_user.full_name,
        author_avatar=current_user.avatar_url,
        author_level=current_user.level
    )

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Toggle Like on a Post."""
    # Check existing like
    query = select(PostLike).where(
        PostLike.user_id == current_user.id,
        PostLike.post_id == post_id
    )
    result = await db.execute(query)
    existing_like = result.scalars().first()
    
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if existing_like:
        await db.delete(existing_like)
        post.like_count -= 1
    else:
        new_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        post.like_count += 1
    
    db.add(post)
    await db.commit()
    return {"status": "success", "likes": post.like_count}

# --- COMMENTS SYSTEM ---

@router.get("/posts/{post_id}/comments", response_model=List[CommentRead])
async def read_post_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get all comments for a post.
    """
    # 1. Fetch Comments + Author Data
    query = (
        select(Comment, User)
        .join(User, Comment.author_id == User.id)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )
    results = await db.execute(query)
    rows = results.all()
    
    # 2. Fetch My Comment Likes
    comment_ids = [row.Comment.id for row in rows]
    my_likes = set()
    if comment_ids:
        likes_query = select(CommentLike.comment_id).where(
            CommentLike.user_id == current_user.id,
            col(CommentLike.comment_id).in_(comment_ids)
        )
        likes_result = await db.execute(likes_query)
        my_likes = set(likes_result.scalars().all())

    # 3. Format Response
    comments_out = []
    for comment, author in rows:
        comments_out.append(CommentRead(
            id=comment.id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            content=comment.content,
            created_at=comment.created_at,
            like_count=comment.like_count,
            is_liked=(comment.id in my_likes),
            author_id=author.id,
            author_name=author.full_name,
            author_avatar=author.avatar_url,
            author_level=author.level
        ))
        
    return comments_out

@router.post("/posts/{post_id}/comments", response_model=CommentRead)
async def create_comment(
    post_id: uuid.UUID,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a comment and update post stats."""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=comment_in.content,
        parent_id=comment_in.parent_id
    )
    db.add(comment)
    
    # Atomic Increment
    post.comment_count += 1
    db.add(post)
    
    await db.commit()
    await db.refresh(comment)
    
    return CommentRead(
        id=comment.id,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        content=comment.content,
        created_at=comment.created_at,
        like_count=0,
        is_liked=False,
        author_id=current_user.id,
        author_name=current_user.full_name,
        author_avatar=current_user.avatar_url,
        author_level=current_user.level
    )

@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Toggle Like on a comment."""
    query = select(CommentLike).where(
        CommentLike.user_id == current_user.id,
        CommentLike.comment_id == comment_id
    )
    result = await db.execute(query)
    existing_like = result.scalars().first()
    
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if existing_like:
        await db.delete(existing_like)
        comment.like_count -= 1
    else:
        new_like = CommentLike(user_id=current_user.id, comment_id=comment_id)
        db.add(new_like)
        comment.like_count += 1
    
    db.add(comment)
    await db.commit()
    
    return {"status": "success", "likes": comment.like_count}