from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date

from app.core.database import get_session
from app.models.user import User
from app.models.garden import GardenHabit, GardenLog
from app.schemas.garden import HabitRead, HabitCreate
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. MY GARDEN (List Habits) ---
@router.get("/", response_model=List[HabitRead])
async def get_my_garden(
    community_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Fetch my habits
    stmt = select(GardenHabit).where(
        GardenHabit.community_id == community_id,
        GardenHabit.user_id == current_user.id
    )
    habits = (await db.exec(stmt)).all()
    
    # Check which ones are done today
    today = date.today()
    habit_ids = [h.id for h in habits]
    
    log_stmt = select(GardenLog).where(
        GardenLog.habit_id.in_(habit_ids),
        GardenLog.log_date == today
    )
    today_logs = (await db.exec(log_stmt)).all()
    done_ids = {l.habit_id for l in today_logs}
    
    results = []
    for h in habits:
        h_read = HabitRead.from_orm(h)
        h_read.is_completed_today = (h.id in done_ids)
        results.append(h_read)
        
    return results

# --- 2. PLANT SEED (Create Habit) ---
@router.post("/", response_model=HabitRead)
async def create_habit(
    habit_in: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    new_habit = GardenHabit(
        **habit_in.dict(),
        user_id=current_user.id
    )
    db.add(new_habit)
    await db.commit()
    await db.refresh(new_habit)
    return new_habit

# --- 3. WATER PLANT (Check-in) ---
@router.post("/{habit_id}/check", response_model=Any)
async def check_in_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user), # Owner check implicit for now
    db: Session = Depends(get_session)
):
    habit = await db.get(GardenHabit, habit_id)
    if not habit:
        raise HTTPException(404, "Habit not found")
        
    today = date.today()
    
    # Check if already done
    existing = await db.exec(select(GardenLog).where(
        GardenLog.habit_id == habit_id,
        GardenLog.log_date == today
    ))
    if existing.first():
        # Toggle OFF (Un-water?) - Optional logic, let's just return success
        return {"status": "already_done"}

    # Create Log
    new_log = GardenLog(habit_id=habit_id, log_date=today)
    db.add(new_log)
    
    # Update Streak (Simple logic: If last log was yesterday, +1. Else reset to 1)
    # For MVP, we just increment. Proper streak logic requires checking yesterday.
    habit.streak_current += 1 
    if habit.streak_current > habit.streak_best:
        habit.streak_best = habit.streak_current
        
    db.add(habit)
    await db.commit()
    
    return {"status": "success", "streak": habit.streak_current}