from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, timezone

from app.api import deps # Consistent dependency injection
from app.models.user import User
from app.models.bunker import BunkerMessage
from app.schemas.bunker import BunkerMessageRead, BunkerMessageCreate

router = APIRouter()

# --- 1. GET LIVE MESSAGES ---
@router.get("/", response_model=List[BunkerMessageRead])
async def get_bunker_feed(
    community_id: str,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Fetch self-destructing messages for the Bunker.
    """
    # Use timezone-aware UTC for modern Python standards
    now = datetime.now(timezone.utc)
    
    # ✅ FIX: Use joinedload(BunkerMessage.author) so we can access author data in the loop
    stmt = (
        select(BunkerMessage)
        .options(joinedload(BunkerMessage.author))
        .where(BunkerMessage.community_id == community_id)
        .where(BunkerMessage.expires_at > now)
        .order_by(BunkerMessage.created_at.desc())
        .limit(50)
    )
    
    # ✅ FIX: Proper Async execution
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    results = []
    for m in messages:
        # Use model_validate for SQLModel/Pydantic v2 or from_orm for v1
        m_read = BunkerMessageRead.model_validate(m) if hasattr(BunkerMessageRead, "model_validate") else BunkerMessageRead.from_orm(m)
        
        # Handle Anonymity (The "Bunker" USP)
        if m.is_anonymous:
            m_read.author_name = "Redacted"
            m_read.author_avatar = None 
        else:
            m_read.author_name = m.author.full_name if m.author else "Unknown"
            m_read.author_avatar = m.author.avatar_url if m.author else None
            
        results.append(m_read)
        
    return results

# --- 2. POST MESSAGE (Burn After Reading) ---
@router.post("/", response_model=BunkerMessageRead)
async def post_bunker_message(
    msg_in: BunkerMessageCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Post a new encrypted/anonymous message with a TTL (Time To Live).
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=msg_in.ttl_seconds)
    
    new_msg = BunkerMessage(
        community_id=msg_in.community_id,
        author_id=current_user.id,
        content=msg_in.content,
        is_anonymous=msg_in.is_anonymous,
        created_at=now,
        expires_at=expires
    )
    
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    
    # Format the response
    res = BunkerMessageRead.model_validate(new_msg) if hasattr(BunkerMessageRead, "model_validate") else BunkerMessageRead.from_orm(new_msg)
    
    if new_msg.is_anonymous:
        res.author_name = "Redacted"
        res.author_avatar = None
    else:
        res.author_name = current_user.full_name
        res.author_avatar = current_user.avatar_url
        
    return res