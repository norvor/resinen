from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.user import User
from app.models.academy import Module, Lesson, LessonCompletion
from app.schemas.academy import ModuleRead, ModuleCreate, LessonCreate
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. GET CURRICULUM (With User Progress) ---
@router.get("/", response_model=List[ModuleRead])
async def get_curriculum(
    community_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # A. Fetch Modules & Lessons (Sorted)
    # Note: SQLModel relationships don't always auto-sort. 
    # For MVP, we fetch modules and trust the relationship load, or sort in Python.
    stmt = select(Module).where(Module.community_id == community_id).order_by(Module.order_index)
    modules = (await db.exec(stmt)).all()
    
    # B. Fetch User's Completed IDs
    # "SELECT lesson_id FROM completion WHERE user_id = me"
    comp_stmt = select(LessonCompletion.lesson_id).where(LessonCompletion.user_id == current_user.id)
    completed_ids = (await db.exec(comp_stmt)).all()
    completed_set = set(completed_ids)

    # C. Assemble & Mark Completed
    result = []
    for mod in modules:
        # Convert module to Pydantic
        # Manually sort lessons inside the module
        sorted_lessons = sorted(mod.lessons, key=lambda l: l.order_index)
        
        # Map to Read Schema and inject 'is_completed'
        lesson_reads = []
        for l in sorted_lessons:
            l_dict = l.dict()
            l_dict['is_completed'] = (l.id in completed_set)
            lesson_reads.append(l_dict)
            
        mod_read = ModuleRead(
            id=mod.id,
            title=mod.title,
            description=mod.description,
            order_index=mod.order_index,
            lessons=lesson_reads
        )
        result.append(mod_read)
        
    return result

# --- 2. MARK LESSON COMPLETE ---
@router.post("/lessons/{lesson_id}/complete", response_model=Any)
async def complete_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Idempotent: If already exists, do nothing
    existing = await db.get(LessonCompletion, (current_user.id, lesson_id))
    if not existing:
        completion = LessonCompletion(user_id=current_user.id, lesson_id=lesson_id)
        db.add(completion)
        
        # Add XP (Gamification hook)
        current_user.xp += 50
        db.add(current_user)
        
        await db.commit()
        
    return {"status": "success"}

# --- 3. ADMIN: CREATE CONTENT (Simplified) ---
@router.post("/modules", response_model=ModuleRead)
async def create_module(mod: ModuleCreate, db: Session = Depends(get_session)):
    new_mod = Module.from_orm(mod)
    db.add(new_mod)
    await db.commit()
    await db.refresh(new_mod)
    return new_mod

@router.post("/modules/{module_id}/lessons", response_model=Any)
async def create_lesson(module_id: str, lesson: LessonCreate, db: Session = Depends(get_session)):
    new_lesson = Lesson(**lesson.dict(), module_id=module_id)
    db.add(new_lesson)
    await db.commit()
    return new_lesson