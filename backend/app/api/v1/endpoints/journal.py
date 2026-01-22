from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from datetime import datetime

from app.api import deps
from app.models.user import User
from app.models.journal import JournalEntry
from pydantic import BaseModel

router = APIRouter()

# --- SCHEMAS (Data Validation) ---
class JournalCreate(BaseModel):
    content: str
    tags: List[str] = []
    stickers: List[Dict] = []
    is_favorite: bool = False

class JournalRead(BaseModel):
    id: uuid.UUID
    content: str
    tags: List[str]
    created_at: datetime
    is_favorite: bool

class JournalUpdate(BaseModel):
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    stickers: Optional[List[Dict]] = None
    is_favorite: Optional[bool] = None

# --- ENDPOINTS ---

@router.get("/", response_model=List[JournalRead])
async def read_journal(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get current user's journal entries (newest first).
    """
    query = select(JournalEntry)\
        .where(JournalEntry.user_id == current_user.id)\
        .order_by(desc(JournalEntry.created_at))\
        .offset(skip)\
        .limit(limit)
        
    result = await db.exec(query)
    return result.all()

@router.post("/", response_model=JournalRead)
async def create_entry(
    entry_in: JournalCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new journal entry.
    """
    new_entry = JournalEntry(
        content=entry_in.content,
        tags=entry_in.tags,
        is_favorite=entry_in.is_favorite,
        user_id=current_user.id
    )
    
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry

@router.put("/{entry_id}", response_model=JournalRead)
async def update_entry(
    entry_id: uuid.UUID,
    entry_update: JournalUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. Find it
    entry = await db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your entry")
    
    # 2. Update fields if provided
    if entry_update.content is not None:
        entry.content = entry_update.content
    if entry_update.tags is not None:
        entry.tags = entry_update.tags
    if entry_update.is_favorite is not None:
        entry.is_favorite = entry_update.is_favorite
        
    entry.updated_at = datetime.utcnow()
    
    # 3. Save
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry

@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete an entry (only if you own it).
    """
    entry = await db.get(JournalEntry, entry_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your entry")
        
    await db.delete(entry)
    await db.commit()
    return {"ok": True}