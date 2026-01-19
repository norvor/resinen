from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.core.database import get_session
from app.models.user import User
from app.models.bunker import BunkerMessage
from app.schemas.bunker import BunkerMessageRead, BunkerMessageCreate
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. GET LIVE MESSAGES ---
@router.get("/", response_model=List[BunkerMessageRead])
async def get_bunker_feed(
    community_id: str,
    db: Session = Depends(get_session)
):
    # Only fetch messages that haven't expired yet
    now = datetime.utcnow()
    stmt = (
        select(BunkerMessage)
        .where(BunkerMessage.community_id == community_id)
        .where(BunkerMessage.expires_at > now)
        .order_by(BunkerMessage.created_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    results = []
    for m in messages:
        m_read = BunkerMessageRead.from_orm(m)
        
        # Handle Anonymity
        if m.is_anonymous:
            m_read.author_name = "Redacted"
            m_read.author_avatar = None # Standard placeholder
        else:
            m_read.author_name = m.author.full_name if m.author else "Unknown"
            m_read.author_avatar = m.author.avatar_url if m.author else None
            
        results.append(m_read)
        
    return results

# --- 2. POST MESSAGE (Burn After Reading) ---
@router.post("/", response_model=BunkerMessageRead)
async def post_bunker_message(
    msg_in: BunkerMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Calculate Expiry
    now = datetime.utcnow()
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
    
    # Return formatted
    res = BunkerMessageRead.from_orm(new_msg)
    if new_msg.is_anonymous:
        res.author_name = "Redacted"
        res.author_avatar = None
    else:
        res.author_name = current_user.full_name
        res.author_avatar = current_user.avatar_url
        
    return res