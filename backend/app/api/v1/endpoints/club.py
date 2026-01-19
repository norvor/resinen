import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone

from app.api import deps
from app.models.user import User
from app.models.club import ClubEvent, ClubRSVP, RSVPStatus
from app.schemas.club import EventRead, EventCreate, RSVPSubmit

router = APIRouter()

# --- 1. LIST EVENTS (Upcoming) ---
@router.get("/", response_model=List[EventRead])
async def list_events(
    community_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Fetch all upcoming club events for the territory."""
    # Use timezone-aware UTC
    now = datetime.now(timezone.utc)
    
    # ✅ FIX: Async execution for events
    stmt = (
        select(ClubEvent)
        .where(ClubEvent.community_id == community_id)
        .where(ClubEvent.start_time > now)
        .order_by(ClubEvent.start_time)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()
    
    # ✅ FIX: Async execution for RSVPs
    event_ids = [e.id for e in events]
    my_rsvps = {}
    
    if event_ids:
        rsvp_stmt = select(ClubRSVP).where(
            ClubRSVP.user_id == current_user.id,
            ClubRSVP.event_id.in_(event_ids)
        )
        rsvp_result = await db.execute(rsvp_stmt)
        my_rsvps = {r.event_id: r.status for r in rsvp_result.scalars().all()}

    # Merge results for the "Paper" UI
    results = []
    for e in events:
        # Compatibility check for SQLModel/Pydantic versioning
        e_read = EventRead.model_validate(e) if hasattr(EventRead, "model_validate") else EventRead.from_orm(e)
        e_read.my_rsvp = my_rsvps.get(e.id)
        results.append(e_read)
        
    return results

# --- 2. CREATE EVENT ---
@router.post("/", response_model=EventRead)
async def create_event(
    evt: EventCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Post a new flyer to the Club board."""
    event_data = evt.model_dump() if hasattr(evt, "model_dump") else evt.dict()
    
    new_event = ClubEvent(
        **event_data,
        creator_id=current_user.id,
        count_going=0
    )
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    return new_event

# --- 3. RSVP ---
@router.post("/{event_id}/rsvp", response_model=Any)
async def rsvp_event(
    event_id: uuid.UUID,
    rsvp_in: RSVPSubmit,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Commit to attending or skip an event."""
    event = await db.get(ClubEvent, event_id)
    if not event:
        raise HTTPException(404, "Event flyer not found on the board")
        
    # Check if exists
    # ✅ FIX: Using select for composite key logic in Async
    stmt = select(ClubRSVP).where(
        ClubRSVP.event_id == event_id,
        ClubRSVP.user_id == current_user.id
    )
    res = await db.execute(stmt)
    existing = res.scalars().first()
    
    was_going = existing and existing.status == RSVPStatus.GOING
    is_going = rsvp_in.status == RSVPStatus.GOING
    
    if existing:
        existing.status = rsvp_in.status
        db.add(existing)
    else:
        new_rsvp = ClubRSVP(event_id=event_id, user_id=current_user.id, status=rsvp_in.status)
        db.add(new_rsvp)
    
    # Update "Awesome" Counter (Paper Delta Logic)
    if is_going and not was_going:
        event.count_going += 1
    elif not is_going and was_going:
        event.count_going = max(0, event.count_going - 1)
        
    db.add(event)
    await db.commit()
    
    return {"status": "success", "going": event.count_going}