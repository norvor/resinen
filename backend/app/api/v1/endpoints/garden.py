import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import date

from app.api import deps # Consistent dependency injection
from app.models.user import User
from app.models.garden import GardenHabit, GardenLog
from app.schemas.garden import HabitRead, HabitCreate

router = APIRouter()

# --- 1. MY GARDEN (List Habits) ---
@router.get("/", response_model=List[HabitRead])
async def get_my_garden(
    community_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Fetch the student's personal garden of habits within this territory."""
    
    # ✅ FIX: Async execution for habits
    stmt = select(GardenHabit).where(
        GardenHabit.community_id == community_id,
        GardenHabit.user_id == current_user.id
    )
    result = await db.execute(stmt)
    habits = result.scalars().all()
    
    # Check which ones are watered (done) today
    today = date.today()
    habit_ids = [h.id for h in habits]
    done_ids = set()
    
    if habit_ids:
        # ✅ FIX: Async execution for logs
        log_stmt = select(GardenLog.habit_id).where(
            GardenLog.habit_id.in_(habit_ids),
            GardenLog.log_date == today
        )
        log_result = await db.execute(log_stmt)
        done_ids = set(log_result.scalars().all())
    
    results = []
    for h in habits:
        # Compatibility check for SQLModel/Pydantic versioning
        h_read = HabitRead.model_validate(h) if hasattr(HabitRead, "model_validate") else HabitRead.from_orm(h)
        h_read.is_completed_today = (h.id in done_ids)
        results.append(h_read)
        
    return results

# --- 2. PLANT SEED (Create Habit) ---
@router.post("/", response_model=HabitRead)
async def create_habit(
    habit_in: HabitCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Plant a new habit seed in the garden."""
    habit_data = habit_in.model_dump() if hasattr(habit_in, "model_dump") else habit_in.dict()
    
    new_habit = GardenHabit(
        **habit_data,
        user_id=current_user.id,
        streak_current=0,
        streak_best=0
    )
    db.add(new_habit)
    await db.commit()
    await db.refresh(new_habit)
    return new_habit

# --- 3. WATER PLANT (Check-in) ---
@router.post("/{habit_id}/check", response_model=Any)
async def check_in_habit(
    habit_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Water a plant (complete a habit) for today to keep the streak alive."""
    
    habit = await db.get(GardenHabit, habit_id)
    if not habit:
        raise HTTPException(404, "Plant (Habit) not found in this garden")
        
    if habit.user_id != current_user.id:
        raise HTTPException(403, "You cannot water someone else's garden")
        
    today = date.today()
    
    # Check if already watered today
    # ✅ FIX: Async execution for existing log check
    stmt = select(GardenLog).where(
        GardenLog.habit_id == habit_id,
        GardenLog.log_date == today
    )
    res = await db.execute(stmt)
    existing = res.scalars().first()
    
    if existing:
        return {"status": "already_done", "streak": habit.streak_current}

    # Create Log
    new_log = GardenLog(habit_id=habit_id, log_date=today)
    db.add(new_log)
    
    # Update Streak Logic
    # (Simple increment for now - in the future, check if yesterday was completed)
    habit.streak_current += 1 
    if habit.streak_current > habit.streak_best:
        habit.streak_best = habit.streak_current
        
    db.add(habit)
    await db.commit()
    
    return {"status": "success", "streak": habit.streak_current}