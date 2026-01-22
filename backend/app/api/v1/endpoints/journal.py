from typing import List, Any
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, col

from app.api import deps
from app.models.user import User
from app.models.journal import JournalEntry
from app.schemas.journal import JournalCreate, JournalRead, JournalUpdate

router = APIRouter()

@router.get("/", response_model=List[JournalRead])
async def read_journal(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    limit: int = 20,
    offset: int = 0,
    tag: str = None # Filter by tag (e.g., "ideas")
):
    """
    Get your personal timeline.
    """
    query = (
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(desc(JournalEntry.created_at))
        .offset(offset)
        .limit(limit)
    )
    
    # Optional: Tag Filtering
    if tag:
        # JSONB containment query for tags
        query = query.where(col(JournalEntry.tags).contains([tag]))

    result = await db.exec(query)
    return result.all()

@router.post("/", response_model=JournalRead)
async def create_entry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    entry_in: JournalCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Log a new thought.
    """
    entry = JournalEntry(
        **entry_in.model_dump(),
        user_id=current_user.id
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry

@router.patch("/{entry_id}", response_model=JournalRead)
async def update_entry(
    entry_id: uuid.UUID,
    entry_in: JournalUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Edit a past entry.
    """
    entry = await db.get(JournalEntry, entry_id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Entry not found")
        
    update_data = entry_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)
        
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
    entry = await db.get(JournalEntry, entry_id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Entry not found")
        
    await db.delete(entry)
    await db.commit()
    return {"status": "deleted"}