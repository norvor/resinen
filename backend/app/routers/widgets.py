from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from pydantic import BaseModel

from ../database import get_session
from ../models import (
    User, BudgetWidget, HabitWidget, ScribbleWidget, TravelWidget, 
    TaskWidget, NoteWidget, LoveWidget, TransmissionWidget, Mission
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/widgets", tags=["widgets"])

# --- DASHBOARD LOAD ---
class DashboardData(BaseModel):
    budget: Optional[BudgetWidget] = None
    habits: Optional[HabitWidget] = None
    scribble: Optional[str] = None
    travel: Optional[TravelWidget] = None
    tasks: List[TaskWidget] = []
    notes: List[NoteWidget] = []
    loves: List[LoveWidget] = []
    transmission: List[TransmissionWidget] = []

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # 1. Fetch Singletons
    budget_res = await session.execute(select(BudgetWidget).where(BudgetWidget.user_id == user.id))
    budget = budget_res.scalars().first()
    
    habit_res = await session.execute(select(HabitWidget).where(HabitWidget.user_id == user.id))
    habits = habit_res.scalars().first()
    
    scribble_res = await session.execute(select(ScribbleWidget).where(ScribbleWidget.user_id == user.id))
    scribble = scribble_res.scalars().first()
    
    travel_res = await session.execute(select(TravelWidget).where(TravelWidget.user_id == user.id))
    travel = travel_res.scalars().first()

    # 2. Fetch Lists
    tasks_res = await session.execute(select(TaskWidget).where(TaskWidget.user_id == user.id))
    tasks = tasks_res.scalars().all()
    
    notes_res = await session.execute(select(NoteWidget).where(NoteWidget.user_id == user.id))
    notes = notes_res.scalars().all()
    
    loves_res = await session.execute(select(LoveWidget).where(LoveWidget.user_id == user.id))
    loves = loves_res.scalars().all()
    
    trans_res = await session.execute(select(TransmissionWidget).where(TransmissionWidget.user_id == user.id))
    transmission = trans_res.scalars().all()

    return {
        "budget": budget,
        "habits": habits,
        "scribble": scribble.content if scribble else "",
        "travel": travel,
        "tasks": tasks,
        "notes": notes,
        "loves": loves,
        "transmission": transmission
    }

# --- BUDGET ---
@router.post("/budget", response_model=BudgetWidget)
async def update_budget(
    data: BudgetWidget, 
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    res = await session.execute(select(BudgetWidget).where(BudgetWidget.user_id == user.id))
    existing = res.scalars().first()
    
    if existing:
        existing.monthly_limit = data.monthly_limit
        existing.spent = data.spent
        existing.currency = data.currency
        session.add(existing)
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        new_budget = BudgetWidget(**data.dict(), user_id=user.id)
        session.add(new_budget)
        await session.commit()
        await session.refresh(new_budget)
        return new_budget

# --- HABITS ---
@router.post("/habits", response_model=HabitWidget)
async def update_habits(
    data: HabitWidget, 
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    res = await session.execute(select(HabitWidget).where(HabitWidget.user_id == user.id))
    existing = res.scalars().first()
    
    if existing:
        existing.grid_data = data.grid_data
        session.add(existing)
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        new_habit = HabitWidget(user_id=user.id, grid_data=data.grid_data)
        session.add(new_habit)
        await session.commit()
        await session.refresh(new_habit)
        return new_habit

# --- SCRIBBLE ---
class ScribblePayload(BaseModel):
    content: str

@router.post("/scribbles")
async def update_scribble(
    payload: ScribblePayload, 
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    res = await session.execute(select(ScribbleWidget).where(ScribbleWidget.user_id == user.id))
    existing = res.scalars().first()
    
    if existing:
        existing.content = payload.content
        session.add(existing)
    else:
        new_scribble = ScribbleWidget(user_id=user.id, content=payload.content)
        session.add(new_scribble)
    
    await session.commit()
    return {"status": "saved"}

# --- TRAVEL ---
@router.post("/travel", response_model=TravelWidget)
async def update_travel(
    data: TravelWidget, 
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    res = await session.execute(select(TravelWidget).where(TravelWidget.user_id == user.id))
    existing = res.scalars().first()
    
    if existing:
        existing.places = data.places
        session.add(existing)
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        new_travel = TravelWidget(user_id=user.id, places=data.places)
        session.add(new_travel)
        await session.commit()
        await session.refresh(new_travel)
        return new_travel

# --- TASKS ---
@router.post("/tasks", response_model=TaskWidget)
async def create_task(t: TaskWidget, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    new_task = TaskWidget(content=t.content, is_done=t.is_done, user_id=user.id)
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return new_task

@router.put("/tasks/{id}", response_model=TaskWidget)
async def update_task(id: int, t: TaskWidget, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(TaskWidget).where(TaskWidget.id == id, TaskWidget.user_id == user.id))
    task = res.scalars().first()
    if not task: raise HTTPException(404)
    task.content = t.content
    task.is_done = t.is_done
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.delete("/tasks/{id}")
async def delete_task(id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(TaskWidget).where(TaskWidget.id == id, TaskWidget.user_id == user.id))
    task = res.scalars().first()
    if task:
        await session.delete(task)
        await session.commit()
    return {"ok": True}

# --- NOTES ---

# NEW: Validation model for partial updates
class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None

@router.post("/notes", response_model=NoteWidget)
async def create_note(n: NoteWidget, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    new_note = NoteWidget(title=n.title, content=n.content, user_id=user.id)
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return new_note

@router.put("/notes/{id}", response_model=NoteWidget)
async def update_note(
    id: int, 
    update_data: NoteUpdate, # Uses the new loose model
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    res = await session.execute(select(NoteWidget).where(NoteWidget.id == id, NoteWidget.user_id == user.id))
    note = res.scalars().first()
    
    if not note: 
        raise HTTPException(404, detail="Note not found")

    # Only update fields that were actually sent
    if update_data.title is not None:
        note.title = update_data.title
    if update_data.content is not None:
        note.content = update_data.content
    if update_data.is_pinned is not None:
        note.is_pinned = update_data.is_pinned
        
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note

@router.delete("/notes/{id}")
async def delete_note(id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(NoteWidget).where(NoteWidget.id == id, NoteWidget.user_id == user.id))
    note = res.scalars().first()
    if note:
        await session.delete(note)
        await session.commit()
    return {"ok": True}

# --- LOVES ---
@router.post("/loves", response_model=LoveWidget)
async def create_love(l: LoveWidget, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    new_love = LoveWidget(name=l.name, category=l.category, description=l.description, link=l.link, user_id=user.id)
    session.add(new_love)
    await session.commit()
    await session.refresh(new_love)
    return new_love

@router.delete("/loves/{id}")
async def delete_love(id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(LoveWidget).where(LoveWidget.id == id, LoveWidget.user_id == user.id))
    love = res.scalars().first()
    if love:
        await session.delete(love)
        await session.commit()
    return {"ok": True}

# --- TRANSMISSION ---
@router.post("/transmission", response_model=TransmissionWidget)
async def create_trans(t: TransmissionWidget, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    new_trans = TransmissionWidget(title=t.title, url=t.url, type=t.type, user_id=user.id)
    session.add(new_trans)
    await session.commit()
    await session.refresh(new_trans)
    return new_trans

@router.delete("/transmission/{id}")
async def delete_trans(id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(TransmissionWidget).where(TransmissionWidget.id == id, TransmissionWidget.user_id == user.id))
    trans = res.scalars().first()
    if trans:
        await session.delete(trans)
        await session.commit()
    return {"ok": True}

@router.get("/missions", response_model=List[Mission])
async def get_missions(
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    # Fetch all missions, ordered by active status then creation
    res = await session.execute(
        select(Mission).where(Mission.user_id == user.id).order_by(Mission.status, Mission.created_at.desc())
    )
    return res.scalars().all()

@router.post("/missions", response_model=Mission)
async def init_mission(
    m: Mission, 
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    # Force user association
    new_mission = Mission(
        codename=m.codename.upper(), # Auto-uppercase codenames
        rune=m.rune,
        color=m.color,
        briefing=m.briefing,
        user_id=user.id
    )
    session.add(new_mission)
    await session.commit()
    await session.refresh(new_mission)
    return new_mission

class MissionUpdate(BaseModel):
    codename: Optional[str] = None
    rune: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    briefing: Optional[str] = None

@router.put("/missions/{id}", response_model=Mission)
async def update_mission(
    id: int, 
    update: MissionUpdate, 
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    res = await session.execute(select(Mission).where(Mission.id == id, Mission.user_id == user.id))
    mission = res.scalars().first()
    
    if not mission: 
        raise HTTPException(404, detail="Mission not found")

    # Apply updates
    if update.codename is not None: mission.codename = update.codename.upper()
    if update.rune is not None: mission.rune = update.rune
    if update.status is not None: mission.status = update.status
    if update.progress is not None: mission.progress = update.progress
    if update.briefing is not None: mission.briefing = update.briefing

    session.add(mission)
    await session.commit()
    await session.refresh(mission)
    return mission

@router.delete("/missions/{id}")
async def abort_mission(
    id: int, 
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    res = await session.execute(select(Mission).where(Mission.id == id, Mission.user_id == user.id))
    mission = res.scalars().first()
    if mission:
        await session.delete(mission)
        await session.commit()
    return {"status": "ABORTED"}