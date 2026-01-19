from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from app.core.database import get_session
from app.models.user import User
from app.models.club import ClubEvent, ClubRSVP, RSVPStatus
from app.schemas.club import EventRead, EventCreate, RSVPSubmit
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. LIST EVENTS (Upcoming) ---
@router.get("/", response_model=List[EventRead])
async def list_events(
    community_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Fetch upcoming events
    now = datetime.utcnow()
    stmt = (
        select(ClubEvent)
        .where(ClubEvent.community_id == community_id)
        .where(ClubEvent.start_time > now) # Only future
        .order_by(ClubEvent.start_time)
    )
    events = (await db.exec(stmt)).all()
    
    # Fetch My RSVPs
    event_ids = [e.id for e in events]
    rsvp_stmt = select(ClubRSVP).where(
        ClubRSVP.user_id == current_user.id,
        ClubRSVP.event_id.in_(event_ids)
    )
    my_rsvps = {r.event_id: r.status for r in (await db.exec(rsvp_stmt)).all()}

    # Merge
    results = []
    for e in events:
        e_read = EventRead.from_orm(e)
        e_read.my_rsvp = my_rsvps.get(e.id)
        results.append(e_read)
        
    return results

# --- 2. CREATE EVENT ---
@router.post("/", response_model=EventRead)
async def create_event(
    evt: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    new_event = ClubEvent(
        **evt.dict(),
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
    event_id: str,
    rsvp_in: RSVPSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    event = await db.get(ClubEvent, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
        
    # Check if exists
    existing = await db.get(ClubRSVP, (event_id, current_user.id))
    
    # Logic for updating count
    # (Simplified: We recalculate or delta update. Let's do delta.)
    
    was_going = existing and existing.status == RSVPStatus.GOING
    is_going = rsvp_in.status == RSVPStatus.GOING
    
    if existing:
        existing.status = rsvp_in.status
        db.add(existing)
    else:
        new_rsvp = ClubRSVP(event_id=event_id, user_id=current_user.id, status=rsvp_in.status)
        db.add(new_rsvp)
    
    # Update Counter
    if is_going and not was_going:
        event.count_going += 1
    elif not is_going and was_going:
        event.count_going = max(0, event.count_going - 1)
        
    db.add(event)
    await db.commit()
    
    return {"status": "success", "going": event.count_going}